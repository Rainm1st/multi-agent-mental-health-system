import { Button, Input, Card, Typography } from "antd";
import { useNavigate } from "react-router-dom";
import { useState } from "react";

const { Title } = Typography;

export default function Login() {
  const [userId, setUserId] = useState("");
  const navigate = useNavigate();

  const handleLogin = () => {
    if (!userId) return;
    localStorage.setItem("user_id", userId);
    navigate("/chat");
  };

  return (
    <div
      style={{
        height: "100vh",
        display: "flex",
        justifyContent: "center",
        alignItems: "center"
      }}
    >
      <Card style={{ width: 360 }}>
        <Title level={3}>Mental Health Assessment</Title>
        <Input
          placeholder="Enter your user ID"
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
        />
        <Button
          type="primary"
          block
          style={{ marginTop: 16 }}
          onClick={handleLogin}
        >
          Login
        </Button>
      </Card>
    </div>
  );
}
