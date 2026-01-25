import { Input, Button, List } from "antd";
import { useState } from "react";

export default function ChatBox() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  const sendMessage = () => {
    if (!input) return;
    setMessages([...messages, { role: "user", text: input }]);
    setInput("");
  };

  return (
    <div style={{ padding: 16 }}>
      <List
        size="small"
        dataSource={messages}
        renderItem={(item) => <List.Item>{item.text}</List.Item>}
        style={{ height: "70vh", overflowY: "auto" }}
      />
      <Input.TextArea
        rows={3}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Type your message..."
      />
      <Button type="primary" block style={{ marginTop: 8 }} onClick={sendMessage}>
        Send
      </Button>
    </div>
  );
}
