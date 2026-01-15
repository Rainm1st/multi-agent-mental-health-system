export default {
  agents: {
    depression: {
      agent_type: "depression",
      risk_level: "high",
      risk_score: 0.85,
      evidence_signals: ["感到空虚", "兴趣减退"],
      confidence: 0.9
    },
    anxiety: {
      agent_type: "anxiety",
      risk_level: "none",
      risk_score: 0.0,
      evidence_signals: [],
      confidence: 0.95
    },
    stress: {
      agent_type: "stress",
      risk_level: "none",
      risk_score: 0.0,
      evidence_signals: [],
      confidence: 1.0
    },
    loneliness: {
      agent_type: "loneliness",
      risk_level: "none",
      risk_score: 0.0,
      evidence_signals: [],
      confidence: 0.95
    }
  },
  coordinator: {
    overall_risk_level: "medium",
    dominant_factors: ["depression"],
    summary:
      "The user shows emotional emptiness and reduced motivation.",
    confidence: 0.88
  }
};
