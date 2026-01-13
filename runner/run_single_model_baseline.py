import json
from pathlib import Path
from openai import OpenAI

# ======================
# 配置
# ======================

MODEL = "qwen-max"
INPUT_FILE = "tests/eval_inputs.json"
OUTPUT_FILE = "results/single_model_results.json"

SYSTEM_PROMPT = """
You are a single-model mental health risk assessment system.

Your task:
- Assess overall psychological risk from the given user text.
- Do NOT perform clinical diagnosis.
- Provide a high-level risk assessment.

You must output a JSON object with EXACTLY the following fields:

{
  "overall_risk_level": "none" | "low" | "medium" | "high",
  "dominant_factors": array of strings chosen from ["depression", "anxiety", "stress", "loneliness"],
  "summary": short string explaining the assessment,
  "confidence": number between 0 and 1
}

Rules:
- All fields are REQUIRED.
- Do NOT add extra fields.
- The output must be valid JSON.
"""

# ======================
# 初始化
# ======================

client = OpenAI(
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# ======================
# 主逻辑
# ======================

def main():
    inputs = json.loads(Path(INPUT_FILE).read_text(encoding="utf-8"))
    results = []

    for item in inputs:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": item["text"]},
        ]

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0,
            response_format={"type": "json_object"},
        )

        output = json.loads(response.choices[0].message.content)

        results.append({
            "id": item["id"],
            "text": item["text"],
            "output": output
        })

    Path("results").mkdir(exist_ok=True)
    Path(OUTPUT_FILE).write_text(
        json.dumps(results, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(f"Baseline results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
