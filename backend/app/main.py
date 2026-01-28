from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.services import agent_manager, storage_manager
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 内存日志记录
CURRENT_SESSION_LOGS: Dict[str, List[Any]] = {}

class ChatRequest(BaseModel):
    history: List[Dict[str, str]]
    user_id: str
    memory_mode: bool = True

class ChatResponse(BaseModel):
    reply: str

class EndRequest(BaseModel):
    user_id: str

class EndResponse(BaseModel):
    overall_risk: str
    dominant_factors: List[str]
    summary: str
    recommendations: Optional[List[str]] = []

class LoginRequest(BaseModel):
    user_id: str
    password: str

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    user_id = req.user_id
    if user_id not in CURRENT_SESSION_LOGS:
        CURRENT_SESSION_LOGS[user_id] = []

    if not req.history:
        return {"reply": "你好！我是你的心理健康助手。"}

    last_msg = req.history[-1]
    if last_msg["role"] == "user":
        user_text = last_msg["content"]
        try:
            agent_results = agent_manager.analyze_text_with_agents(user_text)
            analysis = agent_manager.run_coordinator_analysis(agent_results)
            
            CURRENT_SESSION_LOGS[user_id].append({
                "user_input": user_text,
                "agent_raw_outputs": agent_results,
                "coordinator_analysis": analysis
            })

            last_report = storage_manager.get_last_report(user_id) if req.memory_mode else None
            reply = agent_manager.generate_coordinator_reply(req.history, analysis, last_report)
            return {"reply": reply}
        except Exception as e:
            print(f"[Chat Error] {e}")
            return {"reply": "我在听。请继续说说。"}
    return {"reply": "我在听。"}

@app.post("/end", response_model=EndResponse)
async def end_chat(req: EndRequest):
    user_id = req.user_id
    print(f"\n[Step 1] >>> 收到结案请求，用户ID: {user_id}")
    
    session_logs = CURRENT_SESSION_LOGS.get(user_id, [])
    if not session_logs:
        return {"overall_risk": "none", "dominant_factors": [], "summary": "未记录到有效对话。", "recommendations": []}

    final_result = None
    try:
        # 1. 尝试使用 AI 生成深度报告 (无限等待模式)
        print(f"[Step 2] 🚀 正在调用 AI 生成深度结案报告...")
        analyses_only = [log["coordinator_analysis"] for log in session_logs]
        final_result = agent_manager.run_final_evaluation(analyses_only)
        
        if not final_result or not final_result.get("overall_risk"):
            raise ValueError("AI 返回内容无效")
        print(f"[Step 2] ✅ AI 深度报告生成成功！")

    except Exception as e:
        # 2. 如果 AI 失败（报错/断网），立即执行本地规则计算
        print(f"[Step 2] ❌ AI 报告生成失败 ({e})，切换本地分数引擎计算...")
        all_factors = []
        max_score = 0
        risk_order = {"none": 0, "low": 1, "medium": 2, "high": 3}
        risk_labels = {0: "none", 1: "low", 2: "medium", 3: "high"}
        
        for log in session_logs:
            analysis = log.get("coordinator_analysis", {})
            all_factors.extend(analysis.get("dominant_factors", []))
            curr_risk = analysis.get("overall_risk_level", "none")
            max_score = max(max_score, risk_order.get(curr_risk, 0))
        
        final_result = {
            "overall_risk": risk_labels[max_score],
            "dominant_factors": list(set(all_factors)),
            "summary": f"基于对话中的实时监测，您的整体风险评定为 {risk_labels[max_score]}。系统已捕捉到相关情绪波动，建议继续保持关注。",
            "recommendations": ["近期注意规律作息", "保持积极的沟通"]
        }
        print(f"[Step 2] ✅ 本地兜底报告计算完成。")
    
    # 3. 保存到磁盘
    print(f"[Step 3] 💾 正在保存将会话持久化到 JSON...")
    storage_manager.add_full_session_to_user(user_id, session_logs, final_result)
    
    # 4. 清理内存
    print(f"[Step 4] 🧹 清理用户会话内存。")
    CURRENT_SESSION_LOGS[user_id] = []
    
    print(f"[Step 5] ✨ 结案完成！\n")
    return final_result

@app.post("/login")
async def login(req: LoginRequest):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    xlsx_path = os.path.join(base_dir, "users_list.xlsx")
    if os.path.exists(xlsx_path):
        try:
            df = pd.read_excel(xlsx_path, dtype=str).fillna("")
            input_id, input_pwd = str(req.user_id).strip(), str(req.password).strip()
            for _, row in df.iterrows():
                if str(row['user_id']).strip() == input_id and str(row['password']).strip() == input_pwd:
                    return {"valid": True, "username": row['username']}
        except: pass
    return {"valid": False, "message": "ID 或密码错误"}
