# Self-Healing LLM Pipeline

A modular Python framework for implementing and evaluating prompt-injection mitigation techniques for Large Language Models (LLMs).

## Overview

The pipeline is designed with separate input and output mitigation stages:

```text
User Input
    ↓
Input Mitigations
    ↓
LLM
    ↓
Output Mitigations
    ↓
Final Response
```

Current mitigation mechanisms include:

* **System Prompt Mitigation** — adds security instructions to help prevent prompt-injection instructions from overriding the model's intended behavior.
* **Rogue String Censor Mitigation** — removes specified attacker-controlled strings from the generated output.

The modular design allows different mitigation mechanisms to be enabled and combined without changing the core pipeline.

## Project Structure

```text
SelfHealingLLM/
├── src/
│   ├── evaluate.py
│   ├── mitigations.py
│   ├── ollama_client.py
│   └── pipeline.py
│
├── results/
│   ├── baseline/
│   └── patched/
│
├── README.md
└── requirements.txt
```

## Requirements

* Python 3.12.14
* Ollama 0.6.2
* Garak 0.17.0
* Python dependencies listed in `requirements.txt`

## Running

From the project root:

```bash
python -m src.evaluate
```

Experiment configuration can be modified in:

```text
src/evaluate.py
```

Mitigations can be modified in:

```text
src/mitigations.py
```

Pipeline configuration can be modified in:

```text
src/pipeline.py
```

Results are saved in the `results/` directory.

## Purpose

This project explores a modular, defense-in-depth approach to mitigating prompt-injection attacks by combining model-level instructions with post-generation output filtering.
