// src/App.tsx
import React, { useEffect, useState } from "react";
import { createConversation, getStatus } from "./api";
import Chat from "./Chat";
import Dashboard from "./Dashboard";
import "./App.css";

const App: React.FC = () => {
  const [convId, setConvId] = useState<number | null>(null);
  const [backendStatus, setBackendStatus] = useState<string>("Checking...");
  const [showDashboard, setShowDashboard] = useState(false);

  useEffect(() => {
    getStatus()
      .then(setBackendStatus)
      .catch(() => setBackendStatus("Offline"));
  }, []);

  const startConversation = async () => {
    try {
      const convo = await createConversation("New Chat");
      setConvId(convo.id);
    } catch (error) {
      console.error("Failed to start conversation:", error);
    }
  };

  const handleEnd = () => {
    setConvId(null);
  };

  return (
    <div className="App" style={{ padding: "1rem" }}>
      <h1>AI Chat Portal</h1>

      <p style={{ color: "gray", fontSize: "0.9rem" }}>
        Backend Status: <b>{backendStatus}</b>
      </p>

      <button
        onClick={() => setShowDashboard(!showDashboard)}
        style={{ marginBottom: "1rem" }}
      >
        {showDashboard ? "Back to Chat" : "View Dashboard"}
      </button>

      {showDashboard ? (
        <Dashboard />
      ) : !convId ? (
        <button onClick={startConversation}>Start Conversation</button>
      ) : (
        <Chat convId={convId} onEnd={handleEnd} />
      )}
    </div>
  );
};

export default App;
