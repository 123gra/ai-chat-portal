from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message
import openai, os

# Initialize OpenAI API key safely
openai.api_key = os.getenv("OPENAI_API_KEY")

@receiver(post_save, sender=Message)
def generate_message_embedding(sender, instance, created, **kwargs):
    """Automatically generate embeddings when a new message is saved."""
    if not openai.api_key:
        print(" OpenAI API key not found — skipping embedding generation.")
        return

    if created and instance.content and not instance.embedding:
        try:
            response = openai.embeddings.create(
                model="text-embedding-3-small",
                input=instance.content
            )
            instance.embedding = response.data[0].embedding
            instance.save(update_fields=["embedding"])
        except Exception as e:
            print(" Failed to generate embedding:", e)
