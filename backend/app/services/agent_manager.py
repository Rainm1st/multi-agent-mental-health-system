import os
import json
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
AGENT_MODEL = "qwen3-8b"
COORDINATOR_MODEL = "qwen3-max"

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=BASE_URL
)

# Resolve paths relative to the project root
# Assuming this code runs from 'backend/' directory or we find the root
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent # services -> app -> backend -> root
# Actually, let's just find the 'agents' dir relative to this file
# this file is in backend/app/services/
# agents is in agents/ (root)
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
        response = client.chat.completions.create(
            model=AGENT_MODEL,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": text}
            ],
            temperature=0,
            response_format={"type": "json_object"},
            extra_body={"enable_thinking": False}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Error running agent {agent_name}: {e}")
        return {"error": str(e)}

def analyze_text_with_agents(text):
    results = {}
    # Run sequentially for simplicity, can be parallelized
    for agent_name, prompt in AGENTS_PROMPTS.items():
        results[agent_name] = run_agent(agent_name, prompt, text)
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
            extra_body={"enable_thinking": False}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Error running coordinator analysis: {e}")
        return {"error": str(e)}

def generate_coordinator_reply(history, analysis_result):
    # History: list of {role, content}
    # We want to generate a reply that considers the analysis but behaves like a helpful assistant.
    
    system_prompt = f"""You are a compassionate mental health assistant. 
    You have just analyzed the user's latest message and found the following risk profile:
    {json.dumps(analysis_result, ensure_ascii=False)}
    
    Your goal is to respond to the user naturally and empathetically.
    - If the risk is high, be supportive and suggest seeking help if appropriate, but do not be alarmist.
    - If the risk is low, continue the conversation normally.
    - Do NOT explicitly mention "I have analyzed your message and found X score" unless relevant to helping them.
    - Be concise and warm.
    """
    
    messages = [{"role": "system", "content": system_prompt}] + history
    
    try:
        response = client.chat.completions.create(
            model=COORDINATOR_MODEL,
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return "I'm sorry, I'm having trouble responding right now."

def run_final_evaluation(analyses_history):
    # analyses_history: list of coordinator analysis JSONs from the session
    
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
            extra_body={"enable_thinking": False}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"error": str(e)}
