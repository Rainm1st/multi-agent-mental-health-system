from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.services import agent_manager
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory storage for analysis history
# Structure: { "default": [ {analysis_1}, {analysis_2} ... ] }
SESSION_ANALYSES: Dict[str, List[Any]] = {"default": []}

class ChatRequest(BaseModel):
    history: List[Dict[str, str]]
    session_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    reply: str

class EndRequest(BaseModel):
    session_id: Optional[str] = "default"

class EndResponse(BaseModel):
    overall_risk: str
    dominant_factors: List[str]
    summary: str
    recommendations: Optional[List[str]] = []

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    session_id = req.session_id or "default"
    if session_id not in SESSION_ANALYSES:
        SESSION_ANALYSES[session_id] = []

    if not req.history:
        return {"reply": "Hello! How can I help you today?"}

    # Identify the latest user message
    # The frontend appends the user message to history before sending
    last_msg = req.history[-1]
    
    # Only analyze if the last message is from the user
    if last_msg["role"] == "user":
        user_text = last_msg["content"]

        # 1. Run Agents
        agent_results = agent_manager.analyze_text_with_agents(user_text)

        # 2. Run Coordinator Analysis
        analysis = agent_manager.run_coordinator_analysis(agent_results)

        # 3. Store Analysis
        SESSION_ANALYSES[session_id].append(analysis)

        # 4. Generate Reply
        reply = agent_manager.generate_coordinator_reply(req.history, analysis)
    else:
        # If for some reason the last message isn't user, just respond generally
        # This shouldn't happen with the current frontend logic
        reply = "I'm listening."

    return {"reply": reply}

@app.post("/end", response_model=EndResponse)
async def end_chat(req: EndRequest):
    session_id = req.session_id or "default"
    analyses = SESSION_ANALYSES.get(session_id, [])
    
    if not analyses:
        return {
            "overall_risk": "none",
            "dominant_factors": [],
            "summary": "No conversation data found.",
            "recommendations": []
        }

    final_result = agent_manager.run_final_evaluation(analyses)
    
    # Cleanup
    SESSION_ANALYSES[session_id] = []
    
    return final_result

@app.get("/reset")
async def reset_chat(session_id: str = "default"):
    SESSION_ANALYSES[session_id] = []
    return {"status": "cleared"}
