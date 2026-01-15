import os
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# ================== Configuration ==================
BASELINE_MODEL = "qwen-max"  # Same model as coordinator
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
OUTPUT_FILE = "results/single_model_results.json"
# ===================================================

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=BASE_URL
)

# Load coordinator rules to enforce identical output schema
COORDINATOR_RULES = Path(
    "coordinator/coordinator_rules.md"
).read_text(encoding="utf-8")

INPUTS = json.loads(
    Path("tests/eval_inputs.json").read_text(encoding="utf-8")
)


def run_single_model(text):
    """
    Single-model baseline:
    Use the same coordinator prompt, but without agent decomposition.
    """
    response = client.chat.completions.create(
        model=BASELINE_MODEL,
        messages=[
            {"role": "system", "content": COORDINATOR_RULES},
            {"role": "user", "content": text}
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
        final_output = run_single_model(item["text"])
        results.append({
            "id": item["id"],
            "text": item["text"],
            "final_output": final_output
        })

    Path("results").mkdir(exist_ok=True)
    Path(OUTPUT_FILE).write_text(
        json.dumps(results, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print("[OK] Standardized single-model results saved to", OUTPUT_FILE)


if __name__ == "__main__":
    main()
