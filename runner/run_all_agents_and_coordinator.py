import os
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()


# ================== 配置区 ==================
AGENT_MODEL = "qwen3-8b"        # ← Agent 用这个
COORDINATOR_MODEL = "qwen3-max" # ← Coordinator 用这个
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
OUTPUT_FILE = "results/multi_agent_results.json"
# ============================================

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=BASE_URL
)


AGENTS = {
    "depression": Path("agents/depression_agent.md").read_text(encoding="utf-8"),
    "anxiety": Path("agents/anxiety_agent.md").read_text(encoding="utf-8"),
    "stress": Path("agents/stress_agent.md").read_text(encoding="utf-8"),
    "loneliness": Path("agents/loneliness_agent.md").read_text(encoding="utf-8"),
}

COORDINATOR_RULES = Path("coordinator/coordinator_rules.md").read_text(encoding="utf-8")
INPUTS = json.loads(Path("tests/eval_inputs.json").read_text(encoding="utf-8"))

def run_agent(prompt, text):
    response = client.chat.completions.create(
        model=AGENT_MODEL,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": text}
        ],
        temperature=0,
        response_format={"type": "json_object"},
        # Disable thinking mode for non-streaming structured output
        extra_body={"enable_thinking": False}
    )
    return json.loads(response.choices[0].message.content)


def run_coordinator(agent_outputs):
    response = client.chat.completions.create(
        model=COORDINATOR_MODEL,
        messages=[
            {"role": "system", "content": COORDINATOR_RULES},
            {"role": "user", "content": json.dumps(agent_outputs, ensure_ascii=False)}
        ],
        temperature=0,
        response_format={"type": "json_object"},
        # Disable thinking mode for non-streaming structured output
        extra_body={"enable_thinking": False}
    )
    return json.loads(response.choices[0].message.content)


def main():
    results = []

    for item in INPUTS:
        agent_results = {}

        for agent_type, prompt in AGENTS.items():
            agent_results[agent_type] = run_agent(prompt, item["text"])

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

    print(f"[OK] Multi-agent results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
