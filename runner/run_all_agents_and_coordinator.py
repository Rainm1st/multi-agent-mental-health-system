import json
from pathlib import Path
from openai import OpenAI

# ======================
# 基本配置
# ======================

USER_INPUT = "最近压力特别大，晚上一个人待着的时候会觉得很孤独。"

AGENTS = {
    "depression": "agents/depression_agent.md",
    "anxiety": "agents/anxiety_agent.md",
    "stress": "agents/stress_agent.md",
    "loneliness": "agents/loneliness_agent.md",
}

AGENT_MODEL = "qwen-plus"
COORDINATOR_MODEL = "qwen-max"

# ======================
# 初始化 Client
# ======================

client = OpenAI(
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# ======================
# 跑单个 Agent
# ======================

def run_agent(agent_type, agent_file, user_input):
    prompt = Path(agent_file).read_text(encoding="utf-8")
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": user_input},
    ]

    response = client.chat.completions.create(
        model=AGENT_MODEL,
        messages=messages,
        temperature=0,
        response_format={"type": "json_object"},
    )

    return json.loads(response.choices[0].message.content)

# ======================
# 跑 Coordinator
# ======================

def run_coordinator(agent_outputs):
    coordinator_prompt = Path(
        "coordinator/coordinator_rules.md"
    ).read_text(encoding="utf-8")

    messages = [
        {"role": "system", "content": coordinator_prompt},
        {
            "role": "user",
            "content": json.dumps(agent_outputs, ensure_ascii=False),
        },
    ]

    response = client.chat.completions.create(
        model=COORDINATOR_MODEL,
        messages=messages,
        temperature=0,
        response_format={"type": "json_object"},
    )

    return json.loads(response.choices[0].message.content)

# ======================
# 主流程
# ======================

if __name__ == "__main__":
    agent_results = {}

    print("Running agents...\n")

    for agent_type, agent_file in AGENTS.items():
        result = run_agent(agent_type, agent_file, USER_INPUT)
        agent_results[agent_type] = result
        print(f"[{agent_type.upper()}]")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print()

    print("Running coordinator...\n")

    final_result = run_coordinator(agent_results)
    print("[FINAL COORDINATOR OUTPUT]")
    print(json.dumps(final_result, indent=2, ensure_ascii=False))
