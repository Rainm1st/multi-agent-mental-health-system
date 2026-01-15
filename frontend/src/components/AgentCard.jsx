import { Card, Tag } from "antd";

export default function AgentCard({ agent }) {
  return (
    <Card title={agent.agent_type.toUpperCase()} style={{ marginBottom: 12 }}>
      <p>
        Risk Level: <Tag>{agent.risk_level}</Tag>
      </p>
      <p>Risk Score: {agent.risk_score}</p>
      <p>Confidence: {agent.confidence}</p>

      {agent.evidence_signals.length > 0 && (
        <>
          <p>Evidence:</p>
          <ul>
            {agent.evidence_signals.map((e, idx) => (
              <li key={idx}>{e}</li>
            ))}
          </ul>
        </>
      )}
    </Card>
  );
}
