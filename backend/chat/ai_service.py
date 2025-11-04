import os
import json
import requests
import numpy as np
from django.conf import settings
from openai import OpenAI
from .models import Conversation, Message


class AIService:
    """
    Handles AI chat, summarization, and semantic search with
    OpenAI → LM Studio → local fallback.
    """

    def __init__(self):
        # Load from Django settings or .env
        self.openai_api_key = getattr(settings, "OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
        self.lm_studio_url = getattr(
            settings, "LM_STUDIO_URL", os.getenv("LM_STUDIO_URL", "http://localhost:1234/v1/chat/completions")
        )

        # Initialize OpenAI client if key exists
        self.use_openai = bool(self.openai_api_key)
        self.client = None

        if self.use_openai:
            try:
                self.client = OpenAI(api_key=self.openai_api_key)
                print(" Using OpenAI API for AI responses.")
            except Exception as e:
                print(f"OpenAI client initialization failed: {e}")
                self.use_openai = False
        else:
            print(" No OpenAI key found — using LM Studio (local model).")

    # ----------------------------------------------------------------------
    # CHAT WITH CONTEXT
    # ----------------------------------------------------------------------
    def chat_with_context(self, conversation, user_message):
        """Send user message with prior context, get AI reply."""
        history = Message.objects.filter(conversation=conversation).order_by("created_at")
        messages = [{"role": msg.sender, "content": msg.content} for msg in history]
        messages.append({"role": "user", "content": user_message})
        messages.insert(0, {"role": "system", "content": "You are a helpful, concise AI assistant."})

        if self.use_openai and self.client:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f" OpenAI request failed: {e}")
                print("Falling back to LM Studio...")

        return self._use_lm_studio(messages)

    # ----------------------------------------------------------------------
    # LM STUDIO FALLBACK
    # ----------------------------------------------------------------------
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
                print(f" LM Studio error ({response.status_code}): {response.text}")
                return "Local AI model returned an error."

            data = response.json()
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"].strip()

            return "Local AI model did not return a valid response."
        except Exception as e:
            print(f" LM Studio failed: {e}")
            return "AI service is temporarily unavailable. Please try again later."

    # ----------------------------------------------------------------------
    # SUMMARIZATION
    # ----------------------------------------------------------------------
    def summarize_conversation(self, conversation):
        """Generate a short summary + sentiment + keywords."""
        messages = Message.objects.filter(conversation=conversation).order_by("created_at")
        text = "\n".join([f"{m.sender}: {m.content}" for m in messages])

        prompt = (
            f"Summarize this conversation briefly. "
            f"Then extract sentiment (positive/neutral/negative) and 3–5 keywords.\n\n{text}"
        )

        if self.use_openai and self.client:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                )
                summary = response.choices[0].message.content.strip()
                return {
                    "summary": summary,
                    "sentiment": "neutral",
                    "keywords": [],
                }
            except Exception as e:
                print(f"OpenAI summary failed: {e}")

        summary = self._use_lm_studio([{"role": "user", "content": prompt}])
        return {
            "summary": summary,
            "sentiment": "neutral",
            "keywords": [],
        }

    # ----------------------------------------------------------------------
    # EMBEDDINGS + SEMANTIC SEARCH
    # ----------------------------------------------------------------------
    def _get_embedding(self, text: str, dim: int = 128):
        """Get semantic embedding using OpenAI, LM Studio, or fallback."""
        if not text.strip():
            return np.zeros(dim).tolist()

        # Try OpenAI embeddings
        if self.use_openai and self.client:
            try:
                emb = self.client.embeddings.create(
                    model="text-embedding-3-small",
                    input=text
                )
                vec = np.array(emb.data[0].embedding)
                return self._normalize_vector(vec, dim)
            except Exception as e:
                err_str = str(e)
                if "insufficient_quota" in err_str or "429" in err_str:
                    print(" OpenAI quota exceeded — switching to local fallback embeddings.")
                else:
                    print(f" Embedding generation failed: {e}")

        # Try LM Studio embeddings
        try:
            emb_url = f"{self.lm_studio_url.replace('/chat/completions', '')}/embeddings"
            response = requests.post(
                emb_url,
                json={"model": "local-embedding-model", "input": text},
                timeout=10,
            )
            if response.status_code == 200:
                data = response.json()
                if "data" in data and len(data["data"]) > 0:
                    vec = np.array(data["data"][0]["embedding"])
                    return self._normalize_vector(vec, dim)
        except Exception as e:
            print(f" LM Studio embedding fallback failed: {e}")

        # Final fallback: simple numeric embedding (fixed length)
        print(" Using hash-based embedding fallback.")
        arr = np.array([float(ord(c)) / 1000.0 for c in text[:dim]])
        if len(arr) < dim:
            arr = np.pad(arr, (0, dim - len(arr)))
        elif len(arr) > dim:
            arr = arr[:dim]
        return arr.tolist()

    def _normalize_vector(self, vec, dim: int = 128):
        """Resize or pad embedding to consistent dimension length."""
        vec = np.array(vec)
        if len(vec) < dim:
            vec = np.pad(vec, (0, dim - len(vec)))
        elif len(vec) > dim:
            vec = vec[:dim]
        return vec

    def semantic_search(self, query: str, top_k: int = 5):
        """Return top similar conversations based on semantic meaning."""
        query_emb = np.array(self._get_embedding(query))
        if len(query_emb) == 0:
            return []

        scored = []
        for convo in Conversation.objects.all():
            if not convo.ai_summary:
                continue

            convo_emb = np.array(self._get_embedding(convo.ai_summary))
            if len(convo_emb) == 0:
                continue

            sim = self._cosine_similarity(query_emb, convo_emb)
            scored.append((convo, sim))

        scored.sort(key=lambda x: x[1], reverse=True)
        results = [
            {
                "conversation_id": c.id,
                "title": c.title or f"Conversation {c.id}",
                "summary": c.ai_summary,
                "similarity": round(sim, 3),
            }
            for c, sim in scored[:top_k]
        ]
        print(f" Semantic search results: {len(results)} matches.")
        return results

    def _cosine_similarity(self, a, b):
        """Compute cosine similarity between two vectors safely."""
        if len(a) == 0 or len(b) == 0:
            return 0.0
        a = np.array(a)
        b = np.array(b)
        if len(a) != len(b):
            min_len = min(len(a), len(b))
            a, b = a[:min_len], b[:min_len]
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))
