import { Card, Tag } from "antd";

export default function CoordinatorPanel({ data }) {
  return (
    <Card title="Overall Assessment">
      <p>
        Overall Risk: <Tag>{data.overall_risk_level}</Tag>
      </p>

      <p>Dominant Factors:</p>
      <ul>
        {data.dominant_factors.map((f, idx) => (
          <li key={idx}>{f}</li>
        ))}
      </ul>

      <p>{data.summary}</p>
      <p>Confidence: {data.confidence}</p>
    </Card>
  );
}
