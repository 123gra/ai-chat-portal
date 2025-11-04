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

  if (error)
    return <p className="text-red-500 text-center mt-6">{error}</p>;

  if (!stats)
    return <p className="text-gray-400 text-center mt-6">Loading dashboard...</p>;

  return (
    <div className="max-w-md mx-auto p-6 bg-slate-800/50 border border-gray-700 rounded-2xl shadow-xl backdrop-blur-xl">
      <h2 className="text-2xl font-semibold text-blue-400 mb-6 text-center">
        System Dashboard
      </h2>

      <div className="space-y-4 text-gray-200">
        <div className="flex justify-between border-b border-gray-700 pb-2">
          <span>Total Conversations:</span>
          <b className="text-blue-300">{stats.total_conversations}</b>
        </div>
        <div className="flex justify-between border-b border-gray-700 pb-2">
          <span>Active Conversations:</span>
          <b className="text-blue-300">{stats.active_conversations}</b>
        </div>
        <div className="flex justify-between border-b border-gray-700 pb-2">
          <span>Avg Response Time:</span>
          <b className="text-blue-300">{stats.avg_response_time}</b>
        </div>
        <div className="flex justify-between">
          <span>Using Local LLM:</span>
          <b className={stats.local_llm ? "text-green-400" : "text-red-400"}>
            {stats.local_llm ? "Yes" : "No"}
          </b>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
