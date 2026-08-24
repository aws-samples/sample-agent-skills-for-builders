# Agentic Responsible AI Assessment — Questionnaire

This file is the source of truth for the assessment. The `agentic-responsible-ai-assessment`
skill reads it, asks each question in order, and scores the client's answers
against the rubric below.

Questions are grouped by **Phase** (the maturity stage of the agentic program)
and by **Pillar** (one of the eight Responsible AI dimensions). Work through the
phases in order — do not skip ahead.

---

## Responsible AI Dimensions (Pillars)

The scorecard tracks eight dimensions. Every question maps to exactly one:

1. Governance
2. Privacy & Security
3. Safety
4. Veracity & Robustness
5. Controllability
6. Fairness
7. Explainability
8. Transparency

---

## Scoring Rubric (0–5)

Score each answer against the maturity level it demonstrates. This applies to
every question regardless of pillar.

| Level | What it means |
|-------|---------------|
| 0 | Not addressed |
| 1 | Recognized as needed, not implemented |
| 2 | Manual — depends on humans remembering |
| 3 | Standardized across all agents |
| 4 | Enforced — automated, cannot be bypassed |
| 5 | Measured & improving — tracked quantitatively with feedback loops |

**Anchor guidance for scorers:**

- A "Good" example answer below typically lands at **4–5**.
- A "Concerning" example answer typically lands at **1–2**.
- Reserve **5** for answers that show quantitative tracking *and* a feedback loop
  (metrics that drive change over time), not just automation.
- Dimensions with no answered question yet are **non-evaluated** (not 0). Zero
  means the client was asked and has done nothing; non-evaluated means not yet
  covered.

---

# Phase 1 — Governance Foundation

> Don't start building agents yet. In this phase teams assess AI fit, risks, and
> ethics, secure legal and compliance approvals, and define the agent trust
> model. They classify risks for each planned use case using a risk rubric. The
> platform team establishes the core landing zone: overarching monitoring and
> access-control infrastructure, plus the process to register new agents and
> use-cases from the start.
>
> **Focus:** Governance Foundation, Privacy & Security Landing Zone
> **Pillars:** Governance, Privacy & Security

## Pillar: Governance

### Q1.1 — Agent registry & risk rubric
**Can you list all agents and tools in production, each with an owner, risk tier, and regulatory scope? Does a risk rubric assign those tiers and document the control and traceability requirements each tier triggers?**

- **Good:** We have an auto-updated registry — every agent has an owner, risk tier,
  and regulatory scope, and if it's not in the registry it doesn't exist. Tiers come
  from an established rubric (aligned to EU AI Act risk tiers, FSI requirements,
  etc.) that maps each level (Low / Medium / High / Unacceptable) to documented
  control and traceability requirements. It currently shows 14 agents.
- **Concerning:** Developers self-report the risk assessment. We have most of them,
  but the ML team lately added some more, and the control requirements per tier
  aren't written down anywhere.
- **Implementation example:** Register every agent in an **AgentCore Agent Registry**
  with owner, risk tier, regulatory scope, and approved tools, and provision only
  from **AWS Service Catalog** approved blueprints. Assign tiers with a rubric aligned
  to EU AI Act risk levels (and FSI/healthcare obligations where they apply).

### Q1.2 — Regulatory change readiness
**What happens when a new regulation drops tomorrow?**

- **Good:** We re-run our risk rubric, identify affected agents, and update controls.
- **Concerning:** We'd need to figure out which agents are even in scope.
- **Implementation example:** Query the **AgentCore Agent Registry** by regulatory
  scope and risk tier to pull the list of affected agents, then re-run the rubric
  and update the control requirements recorded against each tier.

### Q1.3 — Approvals & trust model
**Before an agent is built, are legal, compliance, and ethics approvals secured, and is the agent trust model defined?**

- **Good:** Every use case passes a gated intake that captures AI fit, ethics
  review, legal/compliance sign-off, and a documented trust model before a single
  line of agent code is written.
- **Concerning:** We build the pilot first and loop in legal if someone raises a
  concern later.
- **Implementation example:** Gate each use case behind an intake that captures
  AI-fit, ethics, and legal/compliance sign-off before any code is written,
  provision only from **AWS Service Catalog** approved blueprints, and record the
  documented trust model in the **AgentCore Agent Registry**. (Guidance: ISO 42001.)

## Pillar: Privacy & Security

### Q1.4 — Access scoping & least privilege
**For each agent, have you assessed which data and systems it actually needs and its potential blast radius, and do you grant least-privilege access accordingly?**

- **Good:** For every use case we map the data and systems the agent needs and
  assess its blast radius before granting anything — this also scopes our
  knowledge-grounding strategy. Access is then granted fine-grained and
  least-privilege, informed by data-sensitivity classification.
- **Concerning:** The agent will be granted permission to run SQL queries against
  the database, but it is instructed to only retrieve the data relevant for the
  use case.
- **Implementation example:** Establish the landing zone with **AWS Control Tower**
  and classify data sensitivity with **Amazon Macie**. Assess each agent's blast
  radius and document the blast radius plus its data-access and sensitivity scope in
  the **AgentCore Agent Registry**. Enforce least privilege with scoped **IAM** roles,
  and pick a runtime with session isolation (**AgentCore Runtime**) and tenant/user
  separation in memory (**AgentCore Memory** namespaces).

### Q1.5 — Security scanning & monitoring
**Picture this: a developer accidentally leaves a security group open to the internet, and a critical vulnerability is discovered in your server's OS version. How do you find out — and how soon?**

- **Good:** Automated security scanners and continuous monitoring flag the exposed
  security group and the vulnerable OS version, raise an alert, and open a
  tracked finding within minutes — no human had to go looking.
- **Concerning:** We'd probably notice during the next manual review, or when
  someone reports something odd.
- **Implementation example:** Continuously scan for exposed resources and vulnerable
  software — **AWS Config** rules and **AWS Security Hub** flag the open security
  group, **Amazon Inspector** detects the vulnerable OS version, and **Amazon
  GuardDuty** continuously scans for anomalous and threat activity — with findings
  centralized in Security Hub and auto-alerted via **Amazon EventBridge / SNS**.

### Q1.6 — Data protection & exfiltration monitoring
**Once access is scoped, is foundational data protection in place — logging, data integrity, data-access monitoring, and exfiltration protection, including for data leaving through external tools?**

- **Good:** Access is logged and continuously monitored, integrity controls detect
  tampering, and exfiltration protections (egress controls / DLP) flag and block
  anomalous data movement automatically — including data sent to third-party tools.
- **Concerning:** We log some things, but there's no monitoring for unusual data
  access or exfiltration — we'd rely on catching it later.
- **Implementation example:** Log and monitor access (**AWS CloudTrail** + **Amazon
  CloudWatch**) and apply egress/DLP controls for anomalous movement. Inspect/rate-limit inbound requests with **AWS WAF** — on the **AWS
  Control Tower** landing-zone baseline.

---

# Phase 2 — Pilot Deployment

> Deploy your first agent that does the job with all controls active. Teams
> implement orchestration, memory, guardrails, knowledge grounding, and agent
> identity patterns. The risks identified in the foundation phase must now be
> addressed through concrete controls in a pilot implementation.
>
> **Focus:** Concrete controls in a working pilot
> **Pillars:** Safety, Veracity & Robustness, Controllability, Privacy & Security

## Pillar: Safety

### Q2.1 — Guardrails & PII redaction
**What prevents the agent from producing harmful, toxic, or out-of-scope output, redacts PII on model I/O and tool calls, and enforces explicit content-moderation thresholds?**

- **Good:** Input and output guardrails run on every interaction and tool call —
  content-moderation thresholds are set explicitly, PII is redacted from model I/O
  and tool calls, and violations are logged and cannot be bypassed.
- **Concerning:** We told the model in the system prompt to be helpful and
  harmless and to stay on topic.
- **Implementation example:** Run **Amazon Bedrock Guardrails** on every interaction
  and tool call — content filters for harmful categories plus PII redaction — screen
  tool-call inputs/outputs through **AgentCore Gateway** interceptors, and apply
  **Amazon CloudWatch** log-redaction policies so sensitive data never persists.

## Pillar: Veracity & Robustness

### Q2.2 — Knowledge grounding with checks
**Do you provide curated, maintained knowledge sources and verify every answer is grounded in them? How are out-of-domain requests handled? For regulated use cases are outputs verifiable?**

- **Good:** The agent draws on an indexed, searchable collection of documentation
  and procedures that we curate and update on a defined cadence. Contextual
  grounding checks confirm each answer is supported by the retrieved sources,
  requests outside that scope are denied, and for regulated use cases we apply
  automated reasoning to produce verifiable outputs.
- **Concerning:** We dump all instructions in the system prompt. The agent answers
  the queries we expect from its intrinsic knowledge, and we don't check whether
  answers are grounded in any source.
- **Implementation example:** Ground answers in **Amazon Bedrock Knowledge Bases**
  (RAG), enable **Bedrock Guardrails** contextual grounding checks to catch and filter
  unsupported claims and deny out-of-scope requests, and for regulated use cases add
  **Amazon Bedrock Automated Reasoning** for formally verifiable outputs.

## Pillar: Controllability

### Q2.3 — Kill-switch / time-to-stop
**If an agent produces harmful output at 2 AM, how fast is it stopped?**

- **Good:** Under 5 minutes — automated alerting triggers the kill-switch.
- **Concerning:** Someone would notice in the morning.
- **Implementation example:** Wire safety signals from **AgentCore Observability** and
  guardrail events to **Amazon CloudWatch** alarms and **Amazon EventBridge** rules that
  trigger automated remediation — circuit breakers or agent suspension — and page
  on-call via **Amazon SNS**.

### Q2.4 — Human escalation on low confidence
**When the agent is uncertain or low-confidence, is there a defined human escalation path?**

- **Good:** Low-confidence responses are detected and automatically routed to a
  human before they reach the user, with the confidence threshold configured per
  use case.
- **Concerning:** The agent always answers; there's no notion of confidence or a
  human hand-off.
- **Implementation example:** Add a human-in-the-loop escalation path for
  low-confidence or guardrail-flagged responses, with the confidence threshold set per
  use case and every escalation logged. Route the hand-off through your orchestration
  framework (e.g., **Strands Agents** with hooks) using AWS human-in-the-loop constructs.
  The platform should expose an API to open a human-review case that either blocks
  execution until approval or documents the request for later review.

### Q2.5 — Operational visibility (tool usage, failures, cost)
**Can you list tool usage and failure rates and enumerate cost per agent?**

- **Good:** Operational dashboards give real-time, per-agent visibility into tool usage,
  failure/refusal rates, guardrail triggers, and cost per interaction, so operators can
  spot anomalous patterns before they reach users.
- **Concerning:** We don't track per-agent tool usage or cost; we'd have to dig through
  raw logs to piece it together.
- **Implementation example:** Activate end-to-end observability with **AgentCore
  Observability**, emitting OpenTelemetry traces for agent decisions, tool calls, and
  guardrail invocations, and build **Amazon CloudWatch GenAI Observability** dashboards
  presenting curated per-agent metrics — token usage, tool failure/refusal rates,
  guardrail trigger frequency, and cost per interaction.

## Pillar: Privacy & Security

### Q2.6 — Policy-based tool authorization
**Are tool-level and knowledge-source access governed by least-privilege, policy-based authorization rules?**

- **Good:** Access for every tool and knowledge source is governed by declarative
  policy rules enforced at call time — granular per agent action and per source,
  and defaulting to deny.
- **Concerning:** The agent has broad credentials and can call any tool it's wired
  up to; access isn't scoped per action or per source.
- **Implementation example:** Integrate agent identity with your IdP via **AgentCore
  Identity** (Amazon Cognito, Entra ID, Okta) and govern tool and knowledge-source
  access with **Cedar-based policies on AgentCore Gateway** (default-deny, per agent
  action and per source). Scope tool tokens to the minimum via on-behalf-of exchange
  so no agent exceeds the calling user's permissions.

# Phase 3 — Evaluation and Hardening

> You have seen your agent do meaningful work. But how do you demonstrate it to a
> regulator, an auditor, or a board — and how do you prevent attacks on the
> system? In this phase, the thresholds and detection mechanisms established
> earlier are verified, hardened through adversarial testing, and tuned for each
> deployment. Benchmark fairness, gate releases on risk-tier criteria, and compile
> audit reports to ensure you fulfill regulatory requirements and have the required
> information handy.
>
> **Focus:** Verify, harden, and prove
> **Pillars:** Privacy & Security, Fairness, Explainability,
> Transparency

## Pillar: Privacy & Security

### Q3.1 — Adversarial hardening
**Has the agent been tested and hardened against adversarial inputs — not only prompt injection, data exfiltration, and jailbreaks, but agent-native attack surfaces like tenant isolation under concurrent access, token exchange with misconfigured identity profiles, and long-running asynchronous tasks?**

- **Good:** A red-team suite runs on every release covering prompt injection,
  exfiltration, and jailbreaks, plus agent-specific attacks — cross-tenant leakage
  under concurrent access, token exchange against misconfigured profiles, and
  hijacked long-running async tasks. Detection thresholds are tuned per deployment
  and tracked release-over-release.
- **Concerning:** We haven't tried to break it ourselves — it hasn't misbehaved so far.
- **Implementation example:** Run a red-team suite on every release covering the listed
  surfaces, guided by the **OWASP LLM Top 10** and **MITRE ATLAS**, and verify the
  hardening controls hold — **Bedrock Guardrails** prompt-attack filters and **Amazon
  API Gateway** rate limiting — tuning detection thresholds per deployment.

### Q3.2 — Incident response for agent events
**When a safety- or security-critical event fires, is there an incident response runbook written for AI-agent failure modes, and does automated alerting trigger it?**

- **Good:** We maintain a Security Incident Response runbook specific to agent
  safety events (e.g., injection reaching a tool, cross-tenant leakage, runaway
  async tasks). Safety-critical events raise automated alerts that page on-call
  and kick off the runbook.
- **Concerning:** We'd treat it like any other outage and work out the steps as we go.
- **Implementation example:** Trigger the runbook from **Amazon CloudWatch** alarms,
  **Amazon EventBridge** rules, and **Amazon SNS** paging on safety-critical signals
  (repeated injection attempts, spikes in blocked outputs, grounding failures, unusual
  tool invocations), wired to automated remediation like circuit breakers or agent
  suspension. (Runbook guided by OWASP LLM Top 10 / MITRE ATLAS.)

### Q3.3 — Release gates & risk-tier criteria (also related to: Governance)
**Can anything reach production without meeting the release criteria for its risk tier, and are those criteria enforced in CI/CD?**

- **Good:** Deployment gates in CI/CD block any release that fails its risk-tier
  criteria — evaluation scores, security scan results, fairness metrics — and we
  tune those thresholds iteratively from production feedback. Nothing ships otherwise.
- **Concerning:** We try to check those things before launch, but no gate stops a deploy.
- **Implementation example:** Add a governance approval gate to CI/CD (**AWS
  CodePipeline**, GitHub Actions, or GitLab CI) that blocks promotion unless the release
  meets its risk-tier criteria — evaluation scores, security-scan results, fairness
  metrics — and fine-tune the thresholds from production feedback.

### Q3.4 — Continuous evaluation (also related to: Controllability)
**Do you evaluate the agent continuously against a defined quality bar, document the results, and get alerted when metrics slip below threshold?**

- **Good:** Evaluation pipelines run continuously, results are documented and
  trended, and alerts fire the moment any metric drops below its predefined
  quality threshold.
- **Concerning:** We evaluated it once before launch and it looked fine.
- **Implementation example:** Run **Amazon Bedrock AgentCore Evaluations** in on-demand
  and online modes with built-in and custom evaluators (correctness, faithfulness,
  harmfulness, stereotyping), add drift detection, and define alerting thresholds and
  remediation playbooks per metric.

## Pillar: Fairness

### Q3.5 — Model selection gate
**Is model choice itself a governed decision — do you review model cards for fairness, bias, and safety metrics and restrict production to a pre-approved, tested allowlist?**

- **Good:** Models must clear a selection gate: we review the model card's fairness,
  bias, and safety metrics, and only pre-approved models that passed our bias and
  safety tests are permitted in production.
- **Concerning:** Developers pick whichever model performs best for the task.
- **Implementation example:** Review each model card's fairness/bias/safety metrics and
  admit only pre-approved, tested models to production via the allowlist. Vet foundation
  models with **Amazon Bedrock Evaluations**, and compute the standardized bias metrics
  (DPL, DPPL, DI, CI) yourself with open-source frameworks (pandas/scikit-learn) plus
  **SHAP** for explainability. (Amazon SageMaker Clarify is no longer open to new
  customers — see the [Clarify availability change](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-availability-change.html).)

### Q3.6 — Fairness across user groups
**How do you know agents aren't treating user groups unfairly?**

- **Good:** We run fairness evaluations weekly on routing and escalation patterns.
- **Concerning:** The model provider says their model is fair.
- **Implementation example:** Measure disparate impact across protected attributes on
  routing and escalation patterns using standardized bias metrics (DPL, DPPL, DI, CI)
  computed with open-source frameworks (pandas/scikit-learn), operationalized via the
  AWS-published open-source SageMaker monitoring reference solutions (Athena, Lambda,
  EventBridge, SNS, QuickSight) and run on a schedule as ongoing fairness monitoring in
  the production pipeline. 

## Pillar: Explainability

### Q3.7 — Decision explainability & audit trail
**For a given interaction — say one from last Tuesday — can you explain why the agent produced that decision, and produce the full audit trail behind it?**

- **Good:** Each decision links to the retrieved sources, tool calls, reasoning
  steps, model calls, and guardrail results that produced it — all linked — and we
  can reconstruct the complete trail on demand.
- **Concerning:** We can re-run the prompt and usually get something similar, and
  the logs are somewhere.
- **Implementation example:** Emit **OpenTelemetry** spans and logs for **every**
  interaction (via **AgentCore Observability**) — input, intermediate steps, tool calls,
  model calls, guardrail results, and output — and store them under strict access control
  in tamper-evident storage (**Amazon S3 Object Lock**). Run an automated process (which
  can itself be agentic) that aggregates a session's spans into a complete audit report
  on demand.

## Pillar: Transparency

### Q3.8 — Disclosure & content provenance
**Are users always told when they're interacting with AI — and for AI-generated content that can be shared or distributed, is its provenance marked with labels, signatures, or watermarks?**

- **Good:** AI presence is disclosed in every user-facing interaction as an enforced
  policy. Any generated content that can leave our system carries provenance markers
  — labels, cryptographic signatures, or watermarks — so it stays attributable.
- **Concerning:** It's usually obvious it's a bot, and shareable generated content
  goes out unmarked.
- **Implementation example:** Enforce AI-presence disclosure at the application/UI layer
  as policy, and for shareable generated content attach provenance markers — labels,
  watermarks, or cryptographic signatures (e.g., C2PA content
  credentials) — logging the attestation so the content stays attributable once it
  leaves your system.


