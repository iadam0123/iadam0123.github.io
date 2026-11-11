# Enterprise AI reference system — threat model (initial)

## Trust boundaries
1. External caller -> Entra JWT validation -> authenticated application API.
2. Tenant and app-role claims -> Azure AI Search document authorization filter.
3. Authorized retrieved data -> Azure OpenAI model context (retrieved data is untrusted).
4. Agent requester -> independent reviewer -> allowlisted executor -> database audit.
5. Service managed identity -> Azure AI Search / Azure OpenAI.
6. Service -> managed PostgreSQL state and evidence records.

## Threat-to-control matrix
| Threat | Implemented design defense | Remaining verification |
| --- | --- | --- |
| Forged/expired tokens | JWKS signature, issuer/audience/tenant/expiry checks | Test live Entra app and JWKS rotation |
| Horizontal tenant data access | Tenant-filtered DB queries and Search prefilter | Live multi-tenant penetration test; separate tenancy if requirements demand |
| Cross-role document retrieval | Role-filtered Search query before generation | Independent ACL-to-index integrity tests |
| Prompt injection in search passages | Explicit untrusted-data instruction and citation limits | Red-team evaluation, robust output policy and tools isolation |
| Unsupported or fabricated source | Reject nonexistent citation IDs, abstain when no passages | Sentence-level citation/faithfulness evaluator |
| Unauthorized agent tool use | App roles, two-person approval, allowlisted actions | External tool gateway and scope validation |
| Duplicate approval/execution | Database row lock, state transition gating | Load/concurrency tests on PostgreSQL |
| Audit manipulation | Persisted audit event records in DB | Append-only/tamper-evident durable audit service still required |
| Secrets disclosure | Managed identity for AI/Search, DB connection as deployment secret | Key Vault integration, rotation, TLS and private networking |
| Excessive spend or denial of service | Bounded input and model output; autoscaling bounds | API rate limits, quotas, alerts and budget controls |
| Sensitive traces | Metrics route disabled by default; no prompt or bearer token logs by design | Azure telemetry filtering and retention audit |

## Risk acceptance
The reference is **not production-approved**. Risk review is required prior to enabling customer data or action-capable tools. Search index administration must never be granted to the runtime API identity. The synthetic governance score is an illustrative triage mechanism, not compliance certification.

## Required external evidence
Provide timestamped deployment manifest, full CI test logs, integrated Azure OpenAI response and trace, Azure Search tenant/ACL isolation test results, encrypted database backup/restore report, OpenTelemetry trace evidence, security testing and independent architecture review.
