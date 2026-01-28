// Configuration
//const API_BASE_URL = "http://127.0.0.1:8000";
const API_BASE_URL = "http://43.143.78.197:8000";
let currentUser = { id: "", name: "" };
let conversationHistory = [];

// DOM Elements
const chatContainer = document.getElementById("chatContainer");
const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");
const endBtn = document.getElementById("endBtn");
const reportModal = document.getElementById("reportModal");
const reportContent = document.getElementById("reportContent");
const loginOverlay = document.getElementById("loginOverlay");

// Login Logic
async function handleLogin() {
    const idInput = document.getElementById("loginId");
    const passwordInput = document.getElementById("loginPassword");
    const id = idInput.value.trim();
    const password = passwordInput.value.trim();
    
    if (!id || !password) {
        alert("请输入 ID 和密码。");
        return;
    }

    try {
        console.log("正在尝试登录, URL:", `${API_BASE_URL}/login`);
        const resp = await fetch(`${API_BASE_URL}/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_id: id, password: password })
        });
        
        if (!resp.ok) {
            const errText = await resp.text();
            throw new Error(`服务器响应错误: ${resp.status} - ${errText}`);
        }

        const data = await resp.json();
        
        if (data.valid) {
            currentUser = { id: id, name: data.username };
            loginOverlay.classList.add("hidden");
            const isMemory = document.getElementById("memoryModeToggle").checked;
            addMessage("Assistant", `欢迎回来，${data.username}。记忆模式已${isMemory ? "开启" : "关闭"}。`);
        } else {
            alert(data.message || "登录失败，请检查 ID 或密码。");
        }
    } catch (error) {
        console.error("登录异常:", error);
        alert(`登录连接失败！\n\n详细原因: ${error.message}\n\n请检查 API 地址是否为: ${API_BASE_URL}`);
    }
}

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

  // 温馨提示计时器：15秒后如果还没回话，显示一条安抚信息
  const warmPromptTimer = setTimeout(() => {
    const loadingMsg = document.getElementById("loadingMessage");
    if (loadingMsg) {
      const warmText = document.createElement("div");
      warmText.className = "message-wrapper assistant";
      warmText.id = "warmPrompt";
      warmText.innerHTML = `
        <div class="message-role">助手</div>
        <div class="message-bubble" style="background-color: #fffbeb; color: #92400e; border: 1px solid #fde68a;">
          思考的内容比较深刻，我正在努力整理思绪，请再稍等我片刻...
        </div>
      `;
      chatContainer.appendChild(warmText);
      chatContainer.scrollTop = chatContainer.scrollHeight;
    }
  }, 15000);

  try {
    const isMemory = document.getElementById("memoryModeToggle").checked;
    const resp = await fetch(`${API_BASE_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ 
        history: conversationHistory,
        user_id: currentUser.id,
        memory_mode: isMemory
      })
    });

    // 清除计时器和安抚信息
    clearTimeout(warmPromptTimer);
    const warmPrompt = document.getElementById("warmPrompt");
    if (warmPrompt) warmPrompt.remove();

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
      body: JSON.stringify({ user_id: currentUser.id })
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
    
    // Clear UI
    chatContainer.innerHTML = `
      <div class="welcome-message">
        <p>你好！我是你的心理健康助手。</p>
        <p>我们可以聊聊你的近况、心情或者任何你想分享的事情。</p>
      </div>
    `;
    
    closeReport();
    
    // Optional: Call backend to clear old session if needed
}

// Event Listeners
userInput.addEventListener("keypress", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});
