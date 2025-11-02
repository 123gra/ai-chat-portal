// src/Chat.tsx
import React, { useState } from "react";
import { sendMessage, endConversation } from "./api";

interface ChatProps {
  convId: number;
  onEnd: () => void;
}

const Chat: React.FC<ChatProps> = ({ convId, onEnd }) => {
  const [messages, setMessages] = useState<{ sender: string; content: string }[]>([]);
  const [input, setInput] = useState("");
  const [ended, setEnded] = useState(false);

  const handleSend = async () => {
    if (!input.trim() || ended) return;

    try {
      const response = await sendMessage(convId, input);
      setMessages((prev) => [
        ...prev,
        { sender: "user", content: input },
        { sender: "ai", content: response.ai.content },
      ]);
      setInput("");
    } catch (err) {
      console.error("Error sending message:", err);
    }
  };

  const handleEndConversation = async () => {
    try {
      const result = await endConversation(convId);
      alert(`Conversation ended. Summary: ${result.summary}`);
      setEnded(true);
      onEnd();
    } catch (err) {
      console.error("Error ending conversation:", err);
    }
  };

  return (
    <div>
      <h2>Conversation #{convId}</h2>

      <div style={{ border: "1px solid #ccc", padding: "1rem", minHeight: "200px" }}>
        {messages.map((msg, i) => (
          <p key={i}>
            <b>{msg.sender}:</b> {msg.content}
          </p>
        ))}
        {ended && <p style={{ color: "gray" }}> This conversation has ended.</p>}
      </div>

      <div style={{ marginTop: "1rem" }}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a message..."
          disabled={ended}
          style={{ width: "60%", marginRight: "10px" }}
        />
        <button onClick={handleSend} disabled={ended}>
          Send
        </button>
        <button
          onClick={handleEndConversation}
          disabled={ended}
          style={{ marginLeft: "10px", backgroundColor: "#f44336", color: "white" }}
        >
          End Chat
        </button>
      </div>
    </div>
  );
};

export default Chat;
