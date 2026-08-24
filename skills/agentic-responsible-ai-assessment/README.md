# Agentic Responsible AI Assessment Skill

A reusable agent skill that walks a client through a structured Responsible AI
(RAI) assessment for agentic systems. The agent asks 20 questions across three
maturity phases, scores each answer 0–5 against a rubric, and renders a live
posture bar chart across eight Responsible AI dimensions after every answer.

## Disclaimer

This skill helps you assess your Responsible AI posture. Note however, that it is
not comprehensive and even perfect scoring does not ensure you are compliant with
any legal obligations. Responsible AI practices vary by industry, please also
consult industry-specific guidances and the [Responsible AI Well-Architected
Lens](https://docs.aws.amazon.com/wellarchitected/latest/responsible-ai-lens/responsible-ai-lens.html).

## Installation

```bash
npx skills add https://github.com/aws-samples/sample-agent-skills-for-builders --skill agentic-responsible-ai-assessment
```

## When to Use

Reference this skill when the user asks to:

- Run a **Responsible AI assessment** or **RAI scorecard** for an agentic system.
- Perform an **agentic AI maturity review** across governance, safety, and fairness.
- Evaluate an agent platform's governance / safety / fairness **posture**.

## Quick Start

Trigger the skill with a natural-language prompt:

```
"Run a Responsible AI assessment"
"Start the RAI scorecard"
"Do an agentic AI maturity review of our platform"
```

The agent reads `references/questionnaire.md`, detects the client render mode,
then asks one question at a time and charts the posture as it goes.

## Assessment Structure

Questions are grouped by **phase** (program maturity stage) and **pillar** (one of
the eight RAI dimensions):

- **Phase 1 — Governance Foundation:** Governance, Privacy & Security
- **Phase 2 — Pilot Deployment:** Safety, Veracity & Robustness, Controllability,
  Privacy & Security
- **Phase 3 — Evaluation and Hardening:** Privacy & Security, Veracity & Robustness,
  Fairness, Explainability, Transparency, Governance

Each answer is scored 0 (not addressed) to 5 (measured & improving with feedback
loops). Dimensions not yet covered are shown as `non-evaluated`, distinct from a
score of 0.

## Supported Clients

The skill detects its host and picks the richest visualization that client can
actually render:

| Client | Type | Posture chart |
|--------|------|---------------|
| Amazon Quick | Desktop | Interactive **Highcharts** HTML artifact (preferred) |
| Kiro (desktop) | Desktop / IDE | **Mermaid** bar chart |
| Claude Desktop | Desktop | **Mermaid** bar chart (Artifact) |
| GitHub Copilot Chat (VS Code) | IDE | **Mermaid** bar chart |
| Kiro CLI | Terminal | **ASCII** bar chart |
| Claude Code | Terminal | **ASCII** bar chart |

ASCII is the universal fallback — if a Highcharts artifact or Mermaid block fails
to render on a given client, the same data is re-rendered as ASCII so the user is
never left without a chart.

## File Structure

```
agentic-responsible-ai-assessment/
├── SKILL.md                   # Skill definition: assessment loop, scoring, chart rendering
├── README.md                  # This file
└── references/
    └── questionnaire.md       # Source of truth: the 20 questions, example answers, rubric
```

## Customizing

To customize the assessment, edit `references/questionnaire.md` (keep the
phase/pillar structure and the 0–5 rubric) or point the skill at your own
questionnaire file — always keeping the same structure and rubric.

See [SKILL.md](./SKILL.md) for the full assessment loop, scoring guidance, client
detection, and posture chart rendering.
