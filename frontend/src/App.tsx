import React, { useEffect, useState } from "react";
import { createConversation, getStatus } from "./api";
import Chat from "./Chat";
import Dashboard from "./Dashboard";
import ConversationIntelligence from "./ConversationIntelligence";

const App: React.FC = () => {
  const [convId, setConvId] = useState<number | null>(null);
  const [backendStatus, setBackendStatus] = useState<string>("Checking...");
  const [showDashboard, setShowDashboard] = useState(false);
  const [showIntelligence, setShowIntelligence] = useState(false);

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
    <div className="min-h-screen flex flex-col items-center justify-start py-10 px-6 bg-gradient-to-br from-slate-900 via-slate-800 to-black text-white">
      <div className="w-full max-w-3xl text-center space-y-2 mb-8">
        <h1 className="text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-cyan-300 to-teal-400 drop-shadow-md">
          AI Conversation Suite
        </h1>
        <p className="text-sm text-gray-400">
          Backend Status:{" "}
          <span
            className={`font-semibold ${
              backendStatus === "Online" ? "text-green-400" : "text-red-400"
            }`}
          >
            {backendStatus}
          </span>
        </p>
      </div>

      <div className="flex flex-wrap justify-center gap-4 mb-10">
        <button
          onClick={() => {
            setShowDashboard(!showDashboard);
            setShowIntelligence(false);
          }}
          className={`px-5 py-2.5 rounded-lg font-semibold transition ${
            showDashboard
              ? "bg-blue-600 hover:bg-blue-700"
              : "bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-indigo-600"
          }`}
        >
          {showDashboard ? "Back to Chat" : "View Dashboard"}
        </button>

        <button
          onClick={() => {
            setShowIntelligence(!showIntelligence);
            setShowDashboard(false);
          }}
          className={`px-5 py-2.5 rounded-lg font-semibold transition ${
            showIntelligence
              ? "bg-indigo-600 hover:bg-indigo-700"
              : "bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700"
          }`}
        >
          {showIntelligence ? "Back to Chat" : "Conversation Intelligence"}
        </button>
      </div>

      <div className="w-full max-w-3xl">
        {showDashboard ? (
          <Dashboard />
        ) : showIntelligence ? (
          <ConversationIntelligence />
        ) : !convId ? (
          <div className="text-center">
            <button
              onClick={startConversation}
              className="px-6 py-3 text-lg font-bold rounded-xl bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 shadow-lg shadow-green-600/30 glow"
            >
              Start New Conversation
            </button>
          </div>
        ) : (
          <Chat convId={convId} onEnd={handleEnd} />
        )}
      </div>
    </div>
  );
};

export default App;
