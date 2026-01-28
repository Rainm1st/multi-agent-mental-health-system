import os
import json
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
AGENT_MODEL = "qwen3-8b"
COORDINATOR_MODEL = "qwen3-max"

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=BASE_URL
)

# Resolve paths relative to the project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

AGENTS_DIR = PROJECT_ROOT / "agents"
COORDINATOR_DIR = PROJECT_ROOT / "coordinator"

def load_prompts():
    agents = {}
    try:
        agents["depression"] = (AGENTS_DIR / "depression_agent.md").read_text(encoding="utf-8")
        agents["anxiety"] = (AGENTS_DIR / "anxiety_agent.md").read_text(encoding="utf-8")
        agents["stress"] = (AGENTS_DIR / "stress_agent.md").read_text(encoding="utf-8")
        agents["loneliness"] = (AGENTS_DIR / "loneliness_agent.md").read_text(encoding="utf-8")
        
        coordinator_rules = (COORDINATOR_DIR / "coordinator_rules.md").read_text(encoding="utf-8")
        return agents, coordinator_rules
    except Exception as e:
        print(f"Error loading prompts: {e}")
        return {}, ""

AGENTS_PROMPTS, COORDINATOR_RULES = load_prompts()

def run_agent(agent_name, prompt, text):
    try:
        # 延长至 120 秒，给模型充分的分析时间
        response = client.chat.completions.create(
            model=AGENT_MODEL,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": text}
            ],
            temperature=0,
            response_format={"type": "json_object"},
            extra_body={"enable_thinking": False},
            timeout=120.0 
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"[Agent] ⚠️ {agent_name} 调用异常: {str(e)}")
        return {"agent_type": agent_name, "risk_score": 0, "risk_level": "none", "reasoning_summary": "timeout"}

def analyze_text_with_agents(text):
    results = {}
    with ThreadPoolExecutor(max_workers=4) as executor:
        future_to_agent = {
            executor.submit(run_agent, name, prompt, text): name 
            for name, prompt in AGENTS_PROMPTS.items()
        }
        for future in future_to_agent:
            agent_name = future_to_agent[future]
            try:
                results[agent_name] = future.result()
            except Exception as e:
                results[agent_name] = {"error": str(e)}
    return results

def run_coordinator_analysis(agent_outputs):
    try:
        response = client.chat.completions.create(
            model=COORDINATOR_MODEL,
            messages=[
                {"role": "system", "content": COORDINATOR_RULES},
                {"role": "user", "content": json.dumps(agent_outputs, ensure_ascii=False)}
            ],
            temperature=0,
            response_format={"type": "json_object"},
            extra_body={"enable_thinking": False},
            timeout=120.0
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"[Coordinator] ⚠️ 汇总分析异常: {str(e)}")
        return {"overall_risk_level": "none", "summary": "系统繁忙，正在努力处理中...", "confidence": 0}

def generate_coordinator_reply(history, analysis_result, last_report=None):
    memory_context = ""
    if last_report:
        memory_context = f"\n[Memory Mode - Last Assessment]: {json.dumps(last_report, ensure_ascii=False)}"

    system_prompt = f"""You are a compassionate mental health assistant. 
    You have just analyzed the user's latest message and found the following risk profile:
    {json.dumps(analysis_result, ensure_ascii=False)}
    {memory_context}
    
    Your goal is to respond to the user naturally and empathetically.
    - If memory context is available, you can subtly refer to progress or consistent patterns from the previous session.
    - If the risk is high, be supportive and suggest seeking help if appropriate.
    - Be concise and warm.
    """
    
    messages = [{"role": "system", "content": system_prompt}] + history
    
    try:
        response = client.chat.completions.create(
            model=COORDINATOR_MODEL,
            messages=messages,
            temperature=0.7,
            timeout=120.0
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"[Reply] ⚠️ 回复生成异常: {str(e)}")
        return "抱歉，由于分析内容较为复杂，我需要更多时间思考。请稍后再试或换个话题。"

def run_final_evaluation(analyses_history):
    prompt = """You are a senior mental health assessment coordinator.
    You have observed a conversation where the following risk assessments were made for each user message:
    
    {analyses_history_json}
    
    Please provide a final summary of the user's overall mental state throughout this session.
    Output MUST be a JSON object with:
    - overall_risk: "none" | "low" | "medium" | "high"
    - dominant_factors: list of strings
    - summary: A paragraph summarizing the trends and key concerns.
    - recommendations: list of brief recommendations.
    """
    
    try:
        response = client.chat.completions.create(
            model=COORDINATOR_MODEL,
            messages=[
                {"role": "user", "content": prompt.replace("{analyses_history_json}", json.dumps(analyses_history, ensure_ascii=False))}
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
            extra_body={"enable_thinking": False},
            timeout=120.0
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"error": str(e)}
