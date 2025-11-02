from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from chat.models import Conversation

class Command(BaseCommand):
    help = "Auto-end conversations idle for more than 10 minutes."

    def handle(self, *args, **options):
        idle_time = timezone.now() - timedelta(minutes=10)
        ended = Conversation.objects.filter(
            status='active', messages__created_at__lt=idle_time
        ).update(status='ended', ended_at=timezone.now())
        self.stdout.write(f"{ended} conversations auto-ended.")
