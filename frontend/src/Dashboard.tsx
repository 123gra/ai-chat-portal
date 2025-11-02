import React, { useEffect, useState } from "react";
import { getDashboard } from "./api";

interface Stats {
  total_conversations: number;
  active_conversations: number;
  avg_response_time: string;
  local_llm: boolean;
}

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<Stats | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getDashboard()
      .then(setStats)
      .catch((err) => setError(err.message));
  }, []);

  if (error) return <p style={{ color: "red" }}>{error}</p>;
  if (!stats) return <p>Loading dashboard...</p>;

  return (
    <div
      style={{
        padding: "1.5rem",
        border: "1px solid #ddd",
        borderRadius: "10px",
        background: "#fafafa",
        width: "fit-content",
        margin: "20px auto",
      }}
    >
      <h2>System Dashboard</h2>
      <p>
        <b>Total Conversations:</b> {stats.total_conversations}
      </p>
      <p>
        <b>Active Conversations:</b> {stats.active_conversations}
      </p>
      <p>
        <b>Average Response Time:</b> {stats.avg_response_time}
      </p>
      <p>
        <b>Using Local LLM:</b> {stats.local_llm ? "Yes" : "No (Using OpenAI)"}
      </p>
    </div>
  );
};

export default Dashboard;
