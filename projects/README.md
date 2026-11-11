# Enterprise AI Architect Employability Evidence — Three Interactive Reference Projects

**Published source:** https://github.com/iadam0123/iadam0123.github.io/tree/main/projects

**Intended public GitHub Pages entry:** https://iadam0123.github.io/projects/

## Scope and maturity
Three interactive, browser-executed reference prototypes based exclusively on synthetic policies and scenarios. These are **not** production systems, actual corporate deployments, or connected generative-AI models. They are demonstrable user experiences designed to show architecture thinking. They require no API keys, tokens, accounts, server, or external third-party dependencies.

### Project 1: Enterprise AI Knowledge Assistant
- Route: `projects/enterprise-knowledge-assistant/`
- Demonstrates role-filtered authorized passages, deterministic lexical scoring, result ordering, and citations.
- Trial: choose **Employee** and ask about prompt-injection incident procedures: restricted security content will not appear. Choose **Security analyst** and rerun.
- Limitations: no vector index, semantic embedding, generation model, identity provider, or persistent knowledge store.
- Production blueprint: OIDC authentication, document ACL ingestion, retrieval security trimming, hybrid search and embeddings, isolated LLM API, answer verification, prompt-injection testing, telemetry, evaluation suite, data retention governance.

### Project 2: Autonomous Enterprise AI Agent
- Route: `projects/autonomous-enterprise-agent/`
- Demonstrates business request intake, policy threshold, fail-closed rejection, human approval, simulated execution, and downloadable JSON events.
- Trial: submit $4,200 and approve; repeat with $12,000 and confirm policy rejection. Try forbidden bypass text.
- Limitations: deterministic state machine, no LLM planner, real external tools, storage, authentication or immutable audit infrastructure.
- Production blueprint: authenticated API gateway, policy decision point, delegated/scoped tool tokens, explicit human approvals, durable event queue, idempotency keys, retries, secrets vault, alerting and append-only tamper-evident audit.

### Project 3: Enterprise AI Governance and Architecture
- Route: `projects/enterprise-ai-governance/`
- Demonstrates transparent weighted risk triage, context-dependent controls, human governance decision, structured JSON export.
- Trial: select restricted data, unsupervised execution and high impact; inspect the high-risk hold decision.
- Limitations: illustrative heuristic, **not** a NIST/ISO certified risk methodology, compliance audit, legal advice or real regulatory assessment.
- Production blueprint: system inventory, risk taxonomy, evidence registry, control ownership, approval workflows, policy-as-code, model evaluation and independent review.

## Architecture decision records
| ADR | Decision | Reason |
| --- | --- | --- |
| 001 | Browser-only synthetic demonstrations | Public evaluator can interact without private accounts, API costs or exposure of secrets. |
| 002 | Explicitly label simulation | Avoid misrepresenting design prototypes as deployed production LLMs. |
| 003 | Authorization before retrieval ranking | Demonstrate fail-closed source filtering and reduce cross-role disclosure. |
| 004 | Human approval before agent execution | Simulate bounded autonomy and accountable decision-making. |
| 005 | Transparent synthetic risk scoring | Allow reviewers to see and challenge the calculation. |

## Security and employability checklist
- [x] Interactive browser source publicly inspectable
- [x] Synthetic sample data
- [x] No secrets or API keys
- [x] Clear simulation and limitations disclosure
- [x] Deterministic test scenarios reproducible manually
- [x] Structured event export and risk evidence
- [ ] Automated regression and security tests
- [ ] Authenticated, tenant-isolated backend
- [ ] Production-grade LLM inference / agent orchestration
- [ ] CI/CD and deployment telemetry
- [ ] Independently verified benchmarks or employer testimonials

**References:** https://www.nist.gov/itl/ai-risk-management-framework ; https://genai.owasp.org/ ; https://learn.microsoft.com/en-us/azure/well-architected/ .

## Suggested interview walkthrough
1. Explain business requirements and trust boundaries.
2. Demonstrate each live interaction and negative test.
3. Show architecture tradeoffs and identify intentional limitations.
4. Describe incremental production implementation and deployment gates.
5. Never imply these synthetic projects constitute verifiable employment or client work.
