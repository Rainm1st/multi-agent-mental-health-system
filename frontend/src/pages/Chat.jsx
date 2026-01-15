import { Layout } from "antd";
import ChatBox from "../components/ChatBox";
import AgentCard from "../components/AgentCard";
import CoordinatorPanel from "../components/CoordinatorPanel";
import mockResponse from "../mock/mockResponse";

const { Sider, Content } = Layout;

export default function Chat() {
  return (
    <Layout style={{ height: "100vh" }}>
      <Sider width={300} theme="light">
        <ChatBox />
      </Sider>

      <Content style={{ padding: 16, display: "flex", gap: 16 }}>
        <div style={{ flex: 2 }}>
          {Object.entries(mockResponse.agents).map(([key, agent]) => (
            <AgentCard key={key} agent={agent} />
          ))}
        </div>

        <div style={{ flex: 1 }}>
          <CoordinatorPanel data={mockResponse.coordinator} />
        </div>
      </Content>
    </Layout>
  );
}
