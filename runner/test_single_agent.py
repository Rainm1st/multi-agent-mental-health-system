import json
from pathlib import Path
from openai import OpenAI

# ==============================
# 配置区（你只需要改这两行）
# ==============================

AGENT_FILE = "agents/loneliness_agent.md"
USER_INPUT = "最近每天都觉得很空，对什么都提不起兴趣。"

# ==============================
# 初始化 Client（不写 key）
# ==============================

client = OpenAI(
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# ==============================
# 读取 Agent Prompt
# ==============================

agent_prompt = Path(AGENT_FILE).read_text(encoding="utf-8")

messages = [
    {"role": "system", "content": agent_prompt},
    {"role": "user", "content": USER_INPUT}
]

# ==============================
# 调用 qwen3
# ==============================

response = client.chat.completions.create(
    model="qwen-plus",
    messages=messages,
    temperature=0,
    response_format={"type": "json_object"}
)


content = response.choices[0].message.content

print("\n========== RAW OUTPUT ==========")
print(content)

print("\n========== PARSED JSON ==========")
try:
    parsed = json.loads(content)
    print(json.dumps(parsed, indent=2, ensure_ascii=False))
except Exception as e:
    print("JSON 解析失败：", e)
