import React, { useState, useEffect, useRef } from "react";
import { sendMessage, endConversation } from "./api";
import axios from "axios";

interface ChatProps {
  convId: number;
  onEnd: () => void;
}

interface Message {
  sender: string;
  content: string;
}

const Chat: React.FC<ChatProps> = ({ convId, onEnd }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [ended, setEnded] = useState(false);
  const [loading, setLoading] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const fetchMessages = async () => {
      try {
        const res = await axios.get(`/api/chat/${convId}/messages/`);
        setMessages(res.data);
      } catch (err) {
        console.error("Error loading conversation:", err);
      } finally {
        setLoading(false);
      }
    };
    if (convId) fetchMessages();
  }, [convId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

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
      window.location.href = "/";
    } catch (err) {
      console.error("Error ending conversation:", err);
    }
  };

  if (loading) {
    return (
      <div className="text-gray-400 text-center p-6 animate-pulse">
        Loading chat...
      </div>
    );
  }

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h2>Conversation #{convId}</h2>
      </div>

      <div className="chat-box">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`chat-row ${
              msg.sender === "user" ? "chat-row-user" : "chat-row-ai"
            }`}
          >
            <div
              className={`chat-bubble ${
                msg.sender === "user" ? "chat-user" : "chat-ai"
              }`}
            >
              <span className="chat-sender">
                {msg.sender === "user" ? "user:" : "ai:"}
              </span>
              <p className="chat-content">{msg.content}</p>
            </div>
          </div>
        ))}
        {ended && (
          <p className="chat-ended italic text-gray-400">
            This conversation has ended.
          </p>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-area">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a message..."
          disabled={ended}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
        />
        <button onClick={handleSend} disabled={ended}>
          Send
        </button>
        <button
          className="end-btn"
          onClick={handleEndConversation}
          disabled={ended}
        >
          End Chat
        </button>
      </div>
    </div>
  );
};

export default Chat;
