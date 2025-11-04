import React, { useState } from "react";
import { searchConversations } from "./api";

const ConversationIntelligence: React.FC = () => {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    const data = await searchConversations(query);
    setResults(data.results || []);
    setLoading(false);
  };

  return (
    <div className="max-w-2xl mx-auto p-6 bg-slate-800/50 border border-gray-700 rounded-2xl shadow-xl backdrop-blur-xl">
      <h2 className="text-2xl font-semibold text-blue-400 mb-4 text-center">
        Conversation Intelligence
      </h2>

      <div className="flex items-center space-x-3 mb-6">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask something about past chats..."
          className="flex-grow p-2 rounded-md bg-gray-800 border border-gray-600 text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-400"
        />
        <button
          onClick={handleSearch}
          className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white font-semibold rounded-md transition"
        >
          {loading ? "Searching..." : "Search"}
        </button>
      </div>

      {loading && <p className="text-gray-400 text-center">Searching...</p>}

      {!loading && results.length > 0 && (
        <div className="space-y-3">
          {results.map((r, idx) => (
            <div
              key={idx}
              className="border border-gray-600 rounded-md p-4 bg-black/20 hover:border-blue-400 transition"
            >
              <p className="text-gray-100 mb-1">
                <b>Message:</b> {r.content}
              </p>
              <p className="text-sm text-gray-400">
                Similarity: {(r.similarity * 100).toFixed(1)}%
              </p>
            </div>
          ))}
        </div>
      )}

      {!loading && results.length === 0 && query && (
        <p className="text-gray-400 text-center mt-4">
          No matching conversations found.
        </p>
      )}
    </div>
  );
};

export default ConversationIntelligence;
