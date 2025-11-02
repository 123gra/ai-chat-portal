import os
import requests
from django.conf import settings
from openai import OpenAI
from .models import Message


class AIService:
    """
    Handles AI chat and summarization with automatic OpenAI → LM Studio fallback.
    """

    def __init__(self):
        # Prefer Django settings if available
        self.openai_api_key = getattr(settings, "OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
        self.lm_studio_url = getattr(settings, "LM_STUDIO_URL", os.getenv("LM_STUDIO_URL", "http://localhost:1234/v1/chat/completions"))

        # Initialize OpenAI client (if API key exists)
        self.use_openai = bool(self.openai_api_key)
        self.client = None

        if self.use_openai:
            try:
                self.client = OpenAI(api_key=self.openai_api_key)
                print(" Using OpenAI API for AI responses.")
            except Exception as e:
                print(f" OpenAI client initialization failed: {e}")
                self.use_openai = False
        else:
            print(" No OpenAI key found — using LM Studio (local model).")

    # --------------------------------------------------------------------------
    # CHAT WITH CONTEXT
    # --------------------------------------------------------------------------
    def chat_with_context(self, conversation, user_message):
        """Send user message with conversation context and get AI reply."""

        # Fetch prior messages to maintain context
        history = Message.objects.filter(conversation=conversation).order_by("created_at")
        messages = [{"role": msg.sender, "content": msg.content} for msg in history]
        messages.append({"role": "user", "content": user_message})

        # Add a system prompt for consistency
        messages.insert(0, {"role": "system", "content": "You are a helpful, concise AI assistant."})

        # Try OpenAI first
        if self.use_openai and self.client:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f" OpenAI request failed: {e}")
                print(" Falling back to LM Studio...")

        # Fallback to local LLM
        return self._use_lm_studio(messages)

    # --------------------------------------------------------------------------
    # LM STUDIO FALLBACK
    # --------------------------------------------------------------------------
    def _use_lm_studio(self, messages):
        """Send messages to LM Studio local API."""
        try:
            response = requests.post(
                self.lm_studio_url,
                json={
                    "model": "local-model",
                    "messages": messages,
                    "temperature": 0.7,
                },
                timeout=30,
            )

            if response.status_code != 200:
                print(f" LM Studio API error ({response.status_code}): {response.text}")
                return "Local AI model returned an error."

            data = response.json()

            # Validate response format
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"].strip()

            return "Local AI model did not return a valid response."

        except Exception as e:
            print(f" LM Studio failed: {e}")
            return "AI service is temporarily unavailable. Please try again later."

    # --------------------------------------------------------------------------
    # CONVERSATION SUMMARIZATION
    # --------------------------------------------------------------------------
    def summarize_conversation(self, conversation):
        """Generate a short summary when the conversation ends."""

        messages = Message.objects.filter(conversation=conversation).order_by("created_at")
        text = "\n".join([f"{m.sender}: {m.content}" for m in messages])
        prompt = f"Summarize the key points of this conversation clearly and concisely:\n{text}"

        # Try OpenAI
        if self.use_openai and self.client:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f" OpenAI summary failed: {e}")
                print(" Falling back to LM Studio for summary...")

        # Fallback summary
        return self._use_lm_studio([{"role": "user", "content": prompt}])
