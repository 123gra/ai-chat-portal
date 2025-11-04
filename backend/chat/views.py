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

# ----------------------------------------------------------------------
# CONVERSATION MANAGEMENT
# ----------------------------------------------------------------------

@api_view(['POST'])
def create_conversation(request):
    """Create a new conversation and close any active ones."""
    title = request.data.get('title', 'New Conversation')

    # Mark existing active convos as ended
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
    """Handle user → AI message exchange."""
    convo = get_object_or_404(Conversation, id=conv_id)
    content = request.data.get('content', '').strip()

    if not content:
        return Response({"error": "Message cannot be empty."}, status=400)

    # Save user message
    user_msg = Message.objects.create(conversation=convo, sender='user', content=content)

    try:
        ai_response = ai.chat_with_context(convo, content)
        ai_msg = Message.objects.create(conversation=convo, sender='ai', content=ai_response)

        convo.status = "active"
        convo.save(update_fields=["status"])

        return Response({
            "user": MessageSerializer(user_msg).data,
            "ai": MessageSerializer(ai_msg).data,
            "conversation_id": convo.id,
        })
    except Exception as e:
        convo.status = "error"
        convo.metadata.update({
            "error": str(e),
            "failed_at": timezone.now().isoformat()
        })
        convo.save(update_fields=["status", "metadata"])
        return Response({"error": str(e)}, status=500)


@api_view(['POST'])
def end_conversation(request, conv_id):
    """End a conversation and generate AI summary."""
    convo = get_object_or_404(Conversation, id=conv_id)

    if convo.status != 'ended':
        convo.status = 'ended'
        convo.ended_at = timezone.now()
        convo.metadata.update({
            "ended_reason": "user_ended",
            "ended_at": convo.ended_at.isoformat()
        })

        try:
            summary_data = ai.summarize_conversation(convo)
            convo.ai_summary = summary_data.get("summary", "")
            convo.metadata["sentiment"] = summary_data.get("sentiment", "neutral")
            convo.metadata["keywords"] = summary_data.get("keywords", [])
        except Exception as e:
            convo.ai_summary = "Summary unavailable due to AI error."
            convo.metadata["summary_error"] = str(e)

        convo.save(update_fields=["status", "ended_at", "ai_summary", "metadata"])

    return Response({
        "status": convo.status,
        "ended_at": convo.ended_at,
        "summary": convo.ai_summary,
        "sentiment": convo.metadata.get("sentiment", "unknown"),
        "keywords": convo.metadata.get("keywords", [])
    })


@api_view(['GET'])
def get_conversations(request):
    """List all conversations."""
    convos = Conversation.objects.all().order_by('-started_at')
    serializer = ConversationSerializer(convos, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_conversation(request, conv_id):
    """Get all messages of a specific conversation (for chat reload)."""
    convo = get_object_or_404(Conversation, id=conv_id)
    convo_data = ConversationSerializer(convo).data
    messages = Message.objects.filter(conversation=convo).order_by('created_at')
    convo_data["messages"] = MessageSerializer(messages, many=True).data
    return Response(convo_data)


@api_view(['GET'])
def dashboard_stats(request):
    """Dashboard analytics for UI."""
    total = Conversation.objects.count()
    active = Conversation.objects.filter(status='active').count()
    ended = Conversation.objects.filter(status='ended').count()

    avg_duration = (
        Conversation.objects
        .filter(ended_at__isnull=False)
        .annotate(duration=ExpressionWrapper(F('ended_at') - F('started_at'), output_field=DurationField()))
        .aggregate(Avg('duration'))['duration__avg']
    )

    recent = Conversation.objects.order_by('-started_at')[:5]
    serializer = ConversationSerializer(recent, many=True)

    return Response({
        "total": total,
        "active": active,
        "ended": ended,
        "avg_duration_mins": round(avg_duration.total_seconds() / 60, 2) if avg_duration else 0,
        "recent": serializer.data
    })


# ----------------------------------------------------------------------
# SYSTEM & INTELLIGENCE ENDPOINTS
# ----------------------------------------------------------------------

@api_view(["GET"])
def system_status(request):
    """Show system configuration and status."""
    data = {
        "status": "ok",
        "ai_mode": getattr(settings, "AI_MODE", "unknown"),
        "openai_enabled": bool(getattr(settings, "OPENAI_API_KEY", "")),
        "lm_studio_url": getattr(settings, "LM_STUDIO_URL", "not configured"),
        "debug": settings.DEBUG,
    }
    return Response(data)


@api_view(["POST"])
def search_conversations(request):
    """Semantic search endpoint."""
    query = request.data.get("query", "").strip()
    if not query:
        return Response({"error": "Query cannot be empty"}, status=400)

    try:
        results = ai.semantic_search(query)
        return Response({"results": results})
    except Exception as e:
        return Response({"error": str(e)}, status=500)

@api_view(['GET'])
def get_messages(request, conv_id):
    convo = get_object_or_404(Conversation, id=conv_id)
    messages = Message.objects.filter(conversation=convo).order_by('created_at')
    serializer = MessageSerializer(messages, many=True)
    return Response(serializer.data)

