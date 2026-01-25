import { useState } from "react";

export default function AgentCard({ data }) {
  const [open, setOpen] = useState(false);

  return (
    <div
      style={{
        border: "1px solid #ddd",
        borderRadius: "6px",
        padding: "12px",
        marginBottom: "12px",
      }}
    >
      <div
        style={{ cursor: "pointer", fontWeight: "bold" }}
        onClick={() => setOpen((v) => !v)}
      >
        {data.agent_type.toUpperCase()} — Risk: {data.risk_level}
      </div>

      {open && (
        <div style={{ marginTop: "8px", fontSize: "14px" }}>
          <div>Risk Score: {data.risk_score}</div>
          <div>Confidence: {data.confidence}</div>

          {data.evidence_signals?.length > 0 && (
            <>
              <div style={{ marginTop: "6px" }}>Evidence:</div>
              <ul>
                {data.evidence_signals.map((e, i) => (
                  <li key={i}>{e}</li>
                ))}
              </ul>
            </>
          )}
        </div>
      )}
    </div>
  );
}
