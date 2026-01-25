import { useState } from "react";
import ChatBox from "../components/ChatBox";
import AgentCard from "../components/AgentCard";
import CoordinatorPanel from "../components/CoordinatorPanel";
import mockResponse from "../mock/mockResponse";

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [showAgents, setShowAgents] = useState(false);

  const handleSend = (text) => {
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setAnalyzing(true);
    setResult(null);
    setShowAgents(false);

    // Simulate analysis delay
    setTimeout(() => {
      setAnalyzing(false);
      setResult(mockResponse);
    }, 1200);
  };

  return (
    <div style={{ display: "flex", gap: "24px", padding: "24px" }}>
      {/* Left: Chat */}
      <div style={{ flex: 1 }}>
        <ChatBox messages={messages} onSend={handleSend} />

        {analyzing && (
          <div style={{ marginTop: "12px", color: "#666" }}>
            Analyzing emotional signals...
          </div>
        )}
      </div>

      {/* Right: Analysis */}
      <div style={{ flex: 1 }}>
        {result && (
          <>
            <CoordinatorPanel data={result.coordinator} />

            <button
              style={{
                marginTop: "12px",
                padding: "6px 12px",
                cursor: "pointer",
              }}
              onClick={() => setShowAgents((v) => !v)}
            >
              {showAgents ? "Hide Agent Details" : "View Agent Details"}
            </button>

            {showAgents && (
              <div style={{ marginTop: "16px" }}>
                {result.agents.map((agent) => (
                  <AgentCard key={agent.agent_type} data={agent} />
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
