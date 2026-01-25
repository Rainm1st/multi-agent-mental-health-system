// Configuration
const API_BASE_URL = "http://127.0.0.1:8000";
let sessionId = "session_" + Math.random().toString(36).substr(2, 9);
let conversationHistory = [];

// DOM Elements
const chatContainer = document.getElementById("chatContainer");
const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");
const endBtn = document.getElementById("endBtn");
const reportModal = document.getElementById("reportModal");
const reportContent = document.getElementById("reportContent");

// Auto-resize textarea
function autoResize(el) {
  el.style.height = 'auto';
  el.style.height = el.scrollHeight + 'px';
}

// Add Message to Chat UI
function addMessage(role, text, isLoading = false) {
  const wrapper = document.createElement("div");
  wrapper.className = `message-wrapper ${role.toLowerCase()}`;
  
  const roleLabel = role === "User" ? "我" : "助手";
  
  let contentHtml = text;
  if (isLoading) {
      contentHtml = `<span class="loading-dots">思考中</span>`;
      wrapper.id = "loadingMessage";
  }

  wrapper.innerHTML = `
    <div class="message-role">${roleLabel}</div>
    <div class="message-bubble">${contentHtml}</div>
  `;
  
  chatContainer.appendChild(wrapper);
  
  // Remove welcome message if it exists
  const welcome = document.querySelector(".welcome-message");
  if (welcome) welcome.remove();

  // Scroll to bottom
  chatContainer.scrollTop = chatContainer.scrollHeight;
}

function removeLoadingMessage() {
    const loading = document.getElementById("loadingMessage");
    if (loading) loading.remove();
}

// Send Message Flow
async function sendMessage() {
  const text = userInput.value.trim();
  if (!text) return;

  // UI Updates
  userInput.value = "";
  userInput.style.height = "auto";
  userInput.disabled = true;
  sendBtn.disabled = true;
  endBtn.disabled = true;

  addMessage("User", text);
  conversationHistory.push({ role: "user", content: text });

  // Show loading
  addMessage("Assistant", "", true);

  try {
    const resp = await fetch(`${API_BASE_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ 
        history: conversationHistory,
        session_id: sessionId 
      })
    });

    if (!resp.ok) throw new Error("Server error");

    const data = await resp.json();
    
    removeLoadingMessage();
    addMessage("Assistant", data.reply);
    conversationHistory.push({ role: "assistant", content: data.reply });

  } catch (error) {
    console.error(error);
    removeLoadingMessage();
    addMessage("Assistant", "抱歉，服务器连接失败。请检查后端服务是否启动。");
  } finally {
    userInput.disabled = false;
    sendBtn.disabled = false;
    endBtn.disabled = false;
    userInput.focus();
  }
}

// End Conversation & Show Report
async function endConversation() {
  if (conversationHistory.length === 0) {
      alert("请先进行对话再生成报告。");
      return;
  }

  endBtn.disabled = true;
  endBtn.innerHTML = '<span class="loading-dots">生成报告中</span>';

  try {
    const resp = await fetch(`${API_BASE_URL}/end`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId })
    });

    const result = await resp.json();
    showReport(result);

  } catch (error) {
    alert("生成报告失败: " + error.message);
  } finally {
    endBtn.disabled = false;
    endBtn.innerHTML = '<span class="btn-text">结束对话 & 生成报告</span>';
  }
}

function showReport(data) {
    const riskMap = {
        "none": { label: "无风险", class: "risk-none" },
        "low": { label: "低风险", class: "risk-low" },
        "medium": { label: "中风险", class: "risk-medium" },
        "high": { label: "高风险", class: "risk-high" }
    };
    
    const riskInfo = riskMap[data.overall_risk] || riskMap["none"];
    
    // Format dominant factors
    const factorsHtml = data.dominant_factors.length > 0 
        ? data.dominant_factors.map(f => `<span class="factor-tag">${translateFactor(f)}</span>`).join("")
        : "<span class='text-gray-500'>无明显主导因素</span>";

    // Format recommendations
    const recsHtml = (data.recommendations && data.recommendations.length > 0)
        ? `<ul style="padding-left: 20px;">${data.recommendations.map(r => `<li>${r}</li>`).join("")}</ul>`
        : "暂无特别建议。";

    reportContent.innerHTML = `
        <div style="text-align: center;">
            <span class="risk-badge ${riskInfo.class}">${riskInfo.label}</span>
        </div>
        
        <div class="report-section">
            <h3>主要影响因素</h3>
            <div class="factors-list">
                ${factorsHtml}
            </div>
        </div>

        <div class="report-section">
            <h3>综合评估</h3>
            <p style="line-height: 1.6; color: #374151;">${data.summary}</p>
        </div>

        <div class="report-section">
            <h3>建议</h3>
            <div style="line-height: 1.6; color: #374151;">${recsHtml}</div>
        </div>
    `;

    reportModal.classList.remove("hidden");
}

function translateFactor(factor) {
    const map = {
        "depression": "抑郁",
        "anxiety": "焦虑",
        "stress": "压力",
        "loneliness": "孤独"
    };
    return map[factor] || factor;
}

function closeReport() {
    reportModal.classList.add("hidden");
}

function restartChat() {
    // Reset local state
    conversationHistory = [];
    sessionId = "session_" + Math.random().toString(36).substr(2, 9);
    
    // Clear UI
    chatContainer.innerHTML = `
      <div class="welcome-message">
        <p>你好！我是你的心理健康助手。</p>
        <p>我们可以聊聊你的近况、心情或者任何你想分享的事情。</p>
      </div>
    `;
    
    closeReport();
    
    // Optional: Call backend to clear old session if needed, strictly not required since we changed session ID
}

// Event Listeners
userInput.addEventListener("keypress", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});
