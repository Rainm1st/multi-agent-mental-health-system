# Multi-Agent Mental Health Risk Assessment System

<p align="center">
  <a href="#english-version">English</a> | 
  <a href="#中文版">中文</a>
</p>

---

## English Version

### Overview

This project implements a **multi-agent architecture** for mental health risk assessment.  
It analyzes user-generated text from multiple psychological perspectives and aggregates the results into a unified, interpretable assessment.

The system is designed for **research and educational purposes only** and does **not** perform clinical diagnosis.

---

### System Architecture

The system consists of two main layers:

#### 1. Specialized Agent Layer

Four independent agents analyze distinct psychological dimensions:

- **Depression Agent**
- **Anxiety Agent**
- **Stress Agent**
- **Loneliness Agent**

Each agent:
- Focuses on a single psychological dimension
- Uses a dedicated prompt
- Produces a structured JSON output under strict schema constraints

This design enables **signal disentanglement** and improves interpretability.

---

#### 2. Coordinator Layer

A coordinator model aggregates all agent outputs and produces the final assessment.

The coordinator:
- Does **not** re-analyze the original user text
- Operates only on agent-level outputs
- Identifies dominant psychological factors
- Generates an overall risk assessment and summary

---

### Model Configuration

- **Agent Models**: `qwen-plus`
- **Coordinator Model**: `qwen-max`
- API access via **DashScope OpenAI-compatible endpoint**

---

### Project Structure
```
mental-multi-agent-system/
├─ agents/
│ ├─ depression_agent.md
│ ├─ anxiety_agent.md
│ ├─ stress_agent.md
│ └─ loneliness_agent.md
├─ coordinator/
│ └─ coordinator_rules.md
├─ runner/
│ ├─ test_single_agent.py
│ ├─ run_all_agents_and_coordinator.py
│ ├─ run_batch_multi_agent.py
│ ├─ run_single_model_baseline.py
│ └─ compare_results.py
├─ tests/
│ ├─ eval_inputs.json
│ └─ sample_user_inputs.md
├─ results/
│ ├─ multi_agent_results.json
│ └─ single_model_results.json
├─ schema/
├─ .gitignore
└─ README.md
```
---

### Experimental Design

To evaluate the effectiveness of the multi-agent architecture, we compare:

1. **Multi-Agent System**  
   Four specialized agents + a coordinator model

2. **Single-Model Baseline**  
   A single large model (`qwen-max`) performing direct assessment

Both systems:
- Use the same input dataset
- Produce outputs with identical JSON schema
- Are evaluated without ground-truth labels

---

### Evaluation Dataset

The evaluation dataset (`tests/eval_inputs.json`) includes:

- Single-dimension psychological expressions
- Mixed and ambiguous mental states
- Low-risk and high-risk textual inputs

This design enables controlled comparison under varying complexity.

---

### Quantitative Comparison Metrics

Since no ground-truth labels are assumed, we focus on proxy metrics:

- **Risk Level Distribution**
- **Number of Dominant Psychological Factors**
- **Confidence Score Distribution**

These metrics evaluate:
- Risk underestimation or overestimation
- Interpretability and factor disentanglement
- Confidence calibration stability

---

### Key Findings

- The single-model baseline tends to **underestimate psychological risk**, assigning low risk levels to most inputs.
- The multi-agent system produces **more cautious and balanced assessments**, frequently identifying medium or high risk.
- The multi-agent architecture better captures **mixed psychological states** through multiple dominant factors.
- Confidence scores from the multi-agent system are **higher and more differentiated**, while maintaining stability.

---

### How to Run

#### Run Multi-Agent Batch Evaluation
```bash
python runner/run_batch_multi_agent.py
```

Run Single-Model Baseline
```bash
python runner/run_single_model_baseline.py
```

Compare Results
```bash
python runner/compare_results.py
```

### Disclaimer

This system is intended for research and educational use only.
It does not provide medical or clinical diagnosis and must not be used for real-world mental health decision-making.

# 多智能体心理风险评估系统

本项目实现了一套 **多智能体（Multi-Agent）心理风险评估系统**，  
通过多个专职智能体从不同心理维度分析用户文本，并由协调器进行统一汇总与解释。

⚠️ 本系统仅用于 **科研与教学目的**，不构成任何医学或临床心理诊断。

---

## 一、系统概述

系统采用 **多智能体架构**，将复杂的心理状态分析任务拆解为多个可解释的子任务，  
从而提高分析的稳定性、可解释性与风险敏感度。

整体流程为：

> 用户文本  
→ 多个专职心理智能体独立分析  
→ 协调器融合结果  
→ 输出整体心理风险评估

---

## 二、系统架构

系统由两层组成：

### 1. 专职智能体层（Agent Layer）

系统包含四个相互独立的心理维度智能体：

- 抑郁智能体（Depression Agent）
- 焦虑智能体（Anxiety Agent）
- 压力智能体（Stress Agent）
- 孤独感智能体（Loneliness Agent）

每个智能体具有以下特点：

- 仅关注 **单一心理维度**
- 使用独立的 Prompt 规则
- 输出结构化 JSON 结果
- 严格遵循统一 Schema，保证一致性与可解释性

该设计有助于实现 **心理信号解耦**，避免单模型混合判断带来的不稳定性。

---

### 2. 协调器层（Coordinator Layer）

协调器负责整合所有智能体的分析结果，并生成最终评估结论。

协调器的特点：

- ❌ 不重新分析原始用户文本  
- ✅ 仅基于各智能体的输出进行推理  
- 识别主导心理因素（可为多个）
- 给出整体风险等级与总结说明

协调器起到的是 **信息融合与决策汇总** 的作用，而非“再次判断”。

---

## 三、模型配置

- 智能体模型：`qwen-plus`
- 协调器模型：`qwen-max`
- 通过 DashScope 提供的 OpenAI 兼容接口调用

---

## 四、项目结构

```
mental-multi-agent-system/
├─ agents/
│ ├─ depression_agent.md
│ ├─ anxiety_agent.md
│ ├─ stress_agent.md
│ └─ loneliness_agent.md
├─ coordinator/
│ └─ coordinator_rules.md
├─ runner/
│ ├─ test_single_agent.py
│ ├─ run_all_agents_and_coordinator.py
│ ├─ run_batch_multi_agent.py
│ ├─ run_single_model_baseline.py
│ └─ compare_results.py
├─ tests/
│ ├─ eval_inputs.json
│ └─ sample_user_inputs.md
├─ results/
│ ├─ multi_agent_results.json
│ └─ single_model_results.json
├─ schema/
├─ .gitignore
└─ README.md
```


### 目录说明

- `agents/`：四个专职心理维度智能体的规则定义
- `coordinator/`：协调器决策与融合规则
- `runner/`：系统运行脚本与实验代码
- `tests/`：评测用输入数据
- `results/`：多智能体与单模型的实验输出结果
- `schema/`：结构化输出定义（预留）
- `README.md`：项目说明文档

---

## 五、实验设计

为评估多智能体架构的有效性，项目设计了对比实验：

### 对比方法

1. **多智能体系统**
   - 四个专职智能体 + 协调器
2. **单模型基线方法**
   - 单一大型模型直接对用户文本进行整体判断

### 对比原则

- 使用 **相同输入数据**
- 输出 **统一 JSON 结构**
- 在 **无真实标签（无 ground truth）** 的前提下进行比较

---

## 六、评测数据集

评测数据集位于 `tests/eval_inputs.json`，包含：

- 单一心理维度的明确表达
- 多维度混合、模糊心理状态
- 低风险与高风险文本样本

该设计用于观察不同系统在 **复杂心理表述场景** 下的行为差异。

---

## 七、定量评估指标

在无真实标签条件下，采用以下代理指标进行比较分析：

- 风险等级分布（low / medium / high）
- 主导心理因素数量
- 置信度统计特征（均值、方差、区间）

用于分析：

- 风险低估 / 高估倾向
- 对混合心理状态的刻画能力
- 系统输出的稳定性与可信度

---

## 八、实验结论概述

实验结果表明：

- 单模型方法倾向于 **低估心理风险**，大量样本被判定为低风险
- 多智能体系统更为谨慎，更多样本被评估为中高风险
- 多智能体系统更频繁识别出 **多个主导心理因素**
- 多智能体系统的置信度更高且区分度更强，同时保持稳定性

---

## 九、运行方式

### 1. 运行多智能体批量评测

```bash
python runner/run_batch_multi_agent.py
```

2. 运行单模型基线评测
```bash
python runner/run_single_model_baseline.py
```
3. 对比实验结果
```bash
python runner/compare_results.py
```

## 十、免责声明

本系统仅用于 科研与教学用途，
不构成任何心理或医学诊断，
不得用于真实心理健康决策或干预场景。

## 十一、许可说明

本项目仅供学术研究与非商业用途使用。


---
