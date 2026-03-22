# Multi-Personality Decision Agent System

A structured AI decision system that combines local reasoning, optional LLM validation, multi-round reflection, personality debate, judge scoring, and final synthesis.

This project is designed to be more than a one-shot prompt app. Instead of asking a model for a single answer and stopping there, it runs a staged decision workflow where each personality produces a position, challenges itself, argues with others, and then gets evaluated by a judge layer before final aggregation.

## Table of Contents

- Overview
- Why This Project Exists
- Core Features
- Agent Characteristics
- System Workflow
- Reflection Depth Levels
- Architecture and Modules
- Project Structure
- Installation
- Configuration
- How to Run
- Web Interface Guide
- CLI Usage
- Output and Logging
- Strengths and Current Limitations
- Roadmap
- Contributing

## Overview

The system simulates a decision committee composed of four distinct personas:

- Light Yagami
- Shin-chan
- Tanjiro
- Squidward

Each persona has its own risk profile, emotional intensity, logic tendency, worldview, decision style, and speaking tone. The workflow allows these personas to produce independent decisions first, then interact through layered reasoning and conflict.

Unlike a plain chatbot flow, this project introduces an explicit process:

1. Local initial decision per persona
2. Optional LLM validation
3. Multi-round reflection (with depth control)
4. Context-aware persona debate
5. Judge scoring and elimination logic
6. Weighted final synthesis

The result is a decision pipeline that is easier to inspect, compare, and iterate.

## Why This Project Exists

Most single-shot LLM decision systems suffer from three common problems:

1. Unstable outputs for similar inputs
2. Poor explainability of how conclusions were formed
3. Weak enforcement of persona behavior

This project addresses those issues by separating concerns:

- Deterministic local logic creates a controllable baseline
- LLM is optional and can be used only as a validator
- Reflection and debate are explicit intermediate stages
- Judge scoring creates a meta-evaluation layer
- Final synthesis uses weighted aggregation instead of simple voting

## Core Features

### 1) Local-first decision engine

Each persona generates an initial decision locally. This allows the system to run in pure local mode without any model calls.

### 2) Optional LLM validation stage

When enabled, LLM is used to validate persona consistency and identify vulnerabilities, not to replace the local core decision engine.

### 3) Multi-round reflection with depth tiers

Reflection is not cosmetic. Different depth levels execute different numbers of reasoning rounds and strategies.

### 4) Context-aware Stage 4 debate

Debate is no longer fixed template repetition. Later rounds parse and react to earlier statements.

### 5) Judge system (Stage 4.5)

A dedicated judge stage evaluates each persona across consistency, realism, and bias, then selects best and worst personas.

### 6) Weighted final synthesis

Final output is computed from confidence and weight signals, not raw majority count.

### 7) Streamlit UI with process visibility

The web app exposes all stages with detailed cards, reflection traces, debate turns, judge results, and final weighted scores.

## Agent Characteristics

This is a decision-focused agent system, not a generic autonomous universal agent.

What makes it agent-like:

- Stage-based state progression
- Persona-level independent reasoning
- Self-critique and revision loops
- Multi-agent interaction
- Meta-evaluation before final output

What it is not (yet):

- A fully autonomous planner that executes open-world toolchains
- A long-term self-learning memory loop that updates policy over time
- A general purpose action-taking agent across arbitrary tasks

In practical terms, it is a strong structured decision agent architecture with clear observability.

## System Workflow

Current implemented flow:

1. Stage 1: Local Initial Decisions
2. Stage 2: LLM Validation (optional)
3. Stage 3: Multi-round Reflection
4. Stage 4: Persona Debate Arena
5. Stage 4.5: Judge Evaluation System
6. Stage 5: Final Weighted Synthesis

### Stage 1 — Local Initial Decisions

For each persona, the local engine computes:

- Decision (Do / Not Do)
- Confidence
- Weight
- Risk score
- Reasoning summary

This stage is fully local and always executed.

### Stage 2 — Optional LLM Validation

If mixed mode is enabled, each local decision is validated for:

- Persona fit
- Logical consistency
- Obvious vulnerabilities

In pure local mode, this stage is skipped by design.

### Stage 3 — Multi-round Reflection

Each persona runs iterative self-review. Depending on depth mode, this includes questioning, deep analysis, devil’s advocate, and failure pre-mortem.

### Stage 4 — Persona Debate

Debates are generated pairwise, but displayed in a “one-vs-three perspective” layout in the UI. Round 2 and Round 3 now use content-aware reactions to earlier text, reducing repetitive template behavior.

### Stage 4.5 — Judge Evaluation

A dedicated judge phase scores personas and outputs:

- Vote distribution
- Per-persona quality metrics
- Best persona
- Worst persona and reason
- Judge recommendation

### Stage 5 — Final Synthesis

The final recommendation is computed from weighted persona outputs and conflict index. This avoids simplistic winner-take-all voting.

## Reflection Depth Levels

Depth is a real execution switch, not just a label.

- quick: Round 1 only
- standard: Round 1 + Round 2
- deep: Round 1 + Round 2 + Round 3
- expert: deep plus Round 4 pre-mortem

Round definitions:

- Round 1: Challenge initial decision
- Round 2: Deep-dive analysis
- Round 3: Devil’s advocate
- Round 4 (expert only): Failure simulation and mitigation planning

## Architecture and Modules

### app.py

Streamlit UI entry point. Handles:

- User input
- Mode toggles (local-only vs mixed)
- Reflection depth selection
- Full stage rendering
- Card-based visualization for Stage 4.5 and Stage 5

### personality.py

Defines persona structure and core behavioral parameters used by local reasoning and dialogue generation.

### agent_engine.py

Local decision engine. Responsible for:

- Risk analysis
- Personality-driven decision output
- Confidence and weight calculation
- Local reasoning text

### agent_reflection.py

Contains:

- Multi-round reflection logic
- Reflection quality analysis
- Debate generation system

Recent behavior improvements include context-aware rebuttal generation so later rounds react to prior statements instead of repeating static templates.

### hybrid_system.py

Workflow orchestrator that executes all stages and packages structured outputs.

### prompt.py

Prompt templates for:

- Persona decision
- Debate phase
- Judge phase

Includes anti-generic voice constraints and persona shaping requirements.

### test.py

Legacy utilities for API calling and parsing. Still useful for compatibility.

### test_hybrid.py

CLI driver for running the modern pipeline in multiple modes.

## Project Structure

```text
app.py
personality.py
prompt.py
agent_engine.py
agent_reflection.py
hybrid_system.py
test.py
test_hybrid.py
README.md

decision_logs/
agent_workflows/
```

## Installation

1. Create and activate a virtual environment (recommended)
2. Install dependencies

```bash
pip install streamlit requests python-dotenv matplotlib
```

If you maintain dependencies in your own environment manager, keep versions pinned for reproducibility.

## Configuration

Create a .env file in project root:

```env
DEEPSEEK_API_KEY=your_api_key_here
```

If you use local-only mode, the key is not required for core pipeline execution.

## How to Run

### Web app

```bash
streamlit run app.py --server.port 8501
```

### CLI (hybrid workflow)

```bash
python test_hybrid.py
```

### CLI local-only mode

```bash
python test_hybrid.py --local-only
```

### CLI simplified mode

```bash
python test_hybrid.py --simple
```

### CLI analysis mode

```bash
python test_hybrid.py --analyze
```

## Web Interface Guide

### Left panel

- Decision question input
- Local-only toggle
- Reflection depth selector
- Run button

### Right panel

- Stage 1–3 detailed workflow expander
- Stage 4 debate arena (one-vs-three perspective)
- Stage 4.5 judge panel
- Stage 5 final recommendation and weighted scores

UI styling has been refined for readability with high-contrast cards and improved metric/table visibility.

## CLI Usage Notes

The CLI is useful for:

- Fast regression checks
- Local-only behavioral validation
- Debugging stage outputs without UI overhead

For large iterative runs, use CLI plus saved workflow artifacts from log folders.

## Output and Logging

Generated artifacts are stored in:

- decision_logs/
- agent_workflows/

Typical observability targets:

- Whether persona decisions converge or diverge
- Reflection stability by depth mode
- Debate conflict intensity patterns
- Judge score distribution
- Final weighted balance between Do and Not Do

## Strengths and Current Limitations

### Strengths

- Clear stage-based architecture
- Strong transparency and inspectability
- Local execution path available
- Reflection depth control with real behavioral differences
- Judge layer adds meta-level quality control
- Improved debate contextuality

### Current limitations

- Still domain-focused on structured decision scenarios
- No long-term memory adaptation loop yet
- No external tool execution planning loop
- Debate remains rule-based generation, not full semantic reasoning graph

## Roadmap

Potential next upgrades:

1. Add persistent memory feedback loop from historical outcomes
2. Introduce configurable judge scoring weights in UI
3. Add benchmark suite for depth mode comparison
4. Add structured export formats for stage-level analytics
5. Add persona strategy mutation across sessions

## Contributing

Contributions are welcome.

Recommended contribution pattern:

1. Open an issue describing goal and expected behavior
2. Implement focused PRs by module (engine, reflection, debate, judge, UI)
3. Include reproducible run command and example output in PR description
4. Keep changes stage-aligned and observable

## Final Notes

This project is best understood as an explainable decision-agent framework with personality simulation, not just a prompt demo.

If your goal is production-level autonomous agent behavior, this repository already provides a strong foundation for that evolution: local reasoning core, multi-stage orchestration, reflection loops, conflict generation, and judge-mediated synthesis.
