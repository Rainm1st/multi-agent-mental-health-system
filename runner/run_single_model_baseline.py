import os
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()


# ================== 配置区 ==================
BASELINE_MODEL = "qwen3-max"
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
OUTPUT_FILE = "results/single_model_results.json"
# ============================================

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=BASE_URL
)


SYSTEM_PROMPT = """
You are a mental health assessment system.
Analyze the user's text and output a JSON assessment.
"""

INPUTS = json.loads(Path("tests/eval_inputs.json").read_text(encoding="utf-8"))

def main():
    results = []

    for item in INPUTS:
        response = client.chat.completions.create(
            model=BASELINE_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": item["text"]}
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )

        results.append({
            "id": item["id"],
            "text": item["text"],
            "final_output": json.loads(response.choices[0].message.content)
        })

    Path("results").mkdir(exist_ok=True)
    Path(OUTPUT_FILE).write_text(
        json.dumps(results, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(f"[OK] Single-model results saved to {OUTPUT_FILE}")

    response = client.chat.completions.create(
    model=BASELINE_MODEL,
    messages=[...],
    temperature=0,
    response_format={"type": "json_object"},
    extra_body={"enable_thinking": False}
    )


if __name__ == "__main__":
    main()
