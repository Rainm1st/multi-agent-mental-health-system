import json
from pathlib import Path
from openai import OpenAI

# ======================
# 配置
# ======================

INPUT_FILE = "tests/eval_inputs.json"
OUTPUT_FILE = "results/multi_agent_results.json"

AGENTS = {
    "depression": "agents/depression_agent.md",
    "anxiety": "agents/anxiety_agent.md",
    "stress": "agents/stress_agent.md",
    "loneliness": "agents/loneliness_agent.md",
}

AGENT_MODEL = "qwen-plus"
COORDINATOR_MODEL = "qwen-max"

# ======================
# 初始化
# ======================

client = OpenAI(
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# ======================
# Agent & Coordinator
# ======================

def run_agent(agent_file, user_text):
    prompt = Path(agent_file).read_text(encoding="utf-8")
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": user_text},
    ]
    response = client.chat.completions.create(
        model=AGENT_MODEL,
        messages=messages,
        temperature=0,
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)

def run_coordinator(agent_outputs):
    coordinator_prompt = Path(
        "coordinator/coordinator_rules.md"
    ).read_text(encoding="utf-8")

    messages = [
        {"role": "system", "content": coordinator_prompt},
        {"role": "user", "content": json.dumps(agent_outputs, ensure_ascii=False)},
    ]

    response = client.chat.completions.create(
        model=COORDINATOR_MODEL,
        messages=messages,
        temperature=0,
        response_format={"type": "json_object"},
    )

    return json.loads(response.choices[0].message.content)

# ======================
# 主逻辑
# ======================

def main():
    inputs = json.loads(Path(INPUT_FILE).read_text(encoding="utf-8"))
    results = []

    for item in inputs:
        agent_results = {}

        for agent_type, agent_file in AGENTS.items():
            agent_results[agent_type] = run_agent(agent_file, item["text"])

        final_output = run_coordinator(agent_results)

        results.append({
            "id": item["id"],
            "text": item["text"],
            "agent_outputs": agent_results,
            "final_output": final_output
        })

    Path("results").mkdir(exist_ok=True)
    Path(OUTPUT_FILE).write_text(
        json.dumps(results, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(f"Multi-agent results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
