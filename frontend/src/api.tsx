export interface Message {
  id?: number;
  sender: "user" | "ai";
  content: string;
  created_at?: string;
}

export interface Conversation {
  id: number;
  title?: string;
  status: string;
  started_at?: string;
  ended_at?: string | null;
  ai_summary?: string | null;
  messages?: Message[];
}

// Use environment variable from Vite for backend URL
const BASE_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";
const BASE = `${BASE_URL}/api/chat`;

// Create new conversation
export async function createConversation(title = "New Conversation") {
  const res = await fetch(`${BASE}/create/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title }),
  });
  if (!res.ok) throw new Error(`Failed to create conversation: ${res.statusText}`);
  return res.json();
}

// Send message
export async function sendMessage(convId: number, content: string) {
  const res = await fetch(`${BASE}/${convId}/send/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content }),
  });
  if (!res.ok) throw new Error(`Failed to send message: ${res.statusText}`);
  return res.json();
}

// Get all conversations
export async function getConversations(): Promise<Conversation[]> {
  const res = await fetch(`${BASE}/`);
  if (!res.ok) throw new Error("Failed to fetch conversations");
  return res.json();
}

// Get a specific conversation
export async function getConversationMessages(convId: number) {
  const res = await fetch(`${BASE}/${convId}/messages/`);
  if (!res.ok) throw new Error("Failed to fetch messages");
  return res.json();
}

// End a conversation
export async function endConversation(convId: number) {
  const res = await fetch(`${BASE}/${convId}/end/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) throw new Error(`Failed to end conversation: ${res.statusText}`);
  return res.json();
}

// Get backend system status
export async function getStatus(): Promise<string> {
  const res = await fetch(`${BASE}/status/`);
  if (!res.ok) throw new Error("Failed to fetch system status");
  const data = await res.json();
  return data.status || "Unknown";
}

// Get dashboard analytics (mapped fields)
export async function getDashboard() {
  const res = await fetch(`${BASE}/dashboard/`);
  if (!res.ok) throw new Error("Failed to fetch dashboard data");

  const data = await res.json();

  // Map backend fields to frontend format
  return {
    total_conversations: data.total,
    active_conversations: data.active,
    avg_response_time: `${data.avg_duration_mins?.toFixed(2)} mins`,
    local_llm: data.using_local_llm || false,
  };
}
// Search conversations
export async function searchConversations(query: string) {
  const res = await fetch(`${BASE}/search/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });
  if (!res.ok) throw new Error("Failed to perform search");
  return res.json();
}

