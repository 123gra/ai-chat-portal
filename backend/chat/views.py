from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db.models import Avg, F, ExpressionWrapper, DurationField
from django.conf import settings
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .ai_service import AIService

ai = AIService()


# --- Conversation Management --- #

@api_view(['POST'])
def create_conversation(request):
    """Create a new conversation (and mark others ended)."""
    title = request.data.get('title', 'New Conversation')

    # Mark previous actives as ended
    Conversation.objects.filter(status='active').update(
        status='ended', ended_at=timezone.now()
    )

    convo = Conversation.objects.create(
        title=title,
        status='active',
        metadata={
            "ai_mode": getattr(settings, "AI_MODE", "unknown"),
            "started_at": timezone.now().isoformat(),
        }
    )

    return Response({
        "id": convo.id,
        "title": convo.title,
        "status": convo.status,
        "ai_mode": convo.metadata["ai_mode"]
    })


@api_view(['POST'])
def send_message(request, conv_id):
    """Handle user message, AI response, and state updates."""
    convo = get_object_or_404(Conversation, id=conv_id)
    content = request.data.get('content', '').strip()

    if not content:
        return Response({"error": "Message content cannot be empty."}, status=400)

    user_msg = Message.objects.create(conversation=convo, sender='user', content=content)

    try:
        ai_response = ai.chat_with_context(convo, content)

        # Detect if AI mode switched mid-conversation
        current_mode = getattr(settings, "AI_MODE", "unknown")
        if convo.metadata.get("ai_mode") != current_mode:
            convo.metadata["ai_mode"] = current_mode
            convo.metadata["switched_at"] = timezone.now().isoformat()

        ai_msg = Message.objects.create(conversation=convo, sender='ai', content=ai_response)
        convo.status = "active"
        convo.save()

        return Response({
            "user": MessageSerializer(user_msg).data,
            "ai": MessageSerializer(ai_msg).data
        })

    except Exception as e:
        convo.status = 'error'
        convo.metadata.update({
            "error": str(e),
            "failed_at": timezone.now().isoformat()
        })
        convo.save()
        return Response({"error": "AI backend failed", "details": str(e)}, status=500)


@api_view(['POST'])
def end_conversation(request, conv_id):
    """Manually end a conversation (called by frontend or auto-end)."""
    convo = get_object_or_404(Conversation, id=conv_id)

    if convo.status != 'ended':
        convo.status = 'ended'
        convo.ended_at = timezone.now()
        convo.metadata.update({
            "ended_reason": "user_ended",
            "ended_at": convo.ended_at.isoformat()
        })

        # Optional: Generate AI summary if desired
        try:
            summary = ai.summarize_conversation(convo)
            convo.ai_summary = summary
        except Exception:
            convo.ai_summary = "Summary unavailable due to AI error."

        convo.save()

    return Response({
        "status": convo.status,
        "ended_at": convo.ended_at,
        "summary": convo.ai_summary
    })


@api_view(['GET'])
def get_conversations(request):
    convos = Conversation.objects.all().order_by('-started_at')
    serializer = ConversationSerializer(convos, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_conversation(request, conv_id):
    convo = get_object_or_404(Conversation, id=conv_id)
    serializer = ConversationSerializer(convo)
    return Response(serializer.data)


@api_view(['GET'])
def dashboard_stats(request):
    total_conversations = Conversation.objects.count()
    active_conversations = Conversation.objects.filter(status='active').count()
    ended_conversations = Conversation.objects.filter(status='ended').count()

    avg_duration = (
        Conversation.objects
        .filter(ended_at__isnull=False)
        .annotate(duration=ExpressionWrapper(F('ended_at') - F('started_at'), output_field=DurationField()))
        .aggregate(Avg('duration'))['duration__avg']
    )

    latest = Conversation.objects.order_by('-started_at')[:5]
    latest_data = ConversationSerializer(latest, many=True).data

    return Response({
        "total": total_conversations,
        "active": active_conversations,
        "ended": ended_conversations,
        "avg_duration_mins": round(avg_duration.total_seconds() / 60, 2) if avg_duration else 0,
        "recent": latest_data
    })


@api_view(["GET"])
def system_status(request):
    """Check backend configuration for OpenAI or LM Studio."""
    data = {
        "status": "ok",
        "ai_mode": getattr(settings, "AI_MODE", "unknown"),
        "openai_enabled": bool(getattr(settings, "OPENAI_API_KEY", "")),
        "lm_studio_url": getattr(settings, "LM_STUDIO_URL", "not configured"),
        "debug": settings.DEBUG,
    }
    return Response(data)
