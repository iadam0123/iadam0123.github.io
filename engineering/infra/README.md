# Azure infrastructure and deployment

This project requires an **Azure subscription and deployment approval**. No Azure resources have been created by this repository commit.

## Recommended topology

Public ingress → Azure Container Apps (FastAPI; Entra role-protected APIs) → Azure OpenAI Responses and embeddings + Azure AI Search with hybrid retrieval + Azure Database for PostgreSQL (durable agent/governance state).

Use **managed identity**, Search Index Data Reader for the API and Cognitive Services OpenAI User for the model; for the indexing utility grant Search Service Contributor and Search Index Data Contributor in a separately controlled administration identity.

Provision:
1. Resource group, Log Analytics, Container Apps environment, ACR, Azure OpenAI/Foundry deployment (chat + embeddings), Azure AI Search (vector-enabled), PostgreSQL Flexible Server, Key Vault.
2. Entra application registration for API with app roles: Knowledge.Reader, Agent.Requester, Agent.Approver, Agent.Executor and Governance.Assessor. Configure v2 token issuer and audience.
3. Private networking, HTTPS, managed identities, RBAC, Key Vault database access and monitoring.
4. Run schema migrations. For a demonstration only, RUN_SCHEMA_CREATE=true creates tables; set false after migration.
5. Execute `python -m scripts.seed_search` with Azure credentials, after specifying index admin roles, sample tenant, model deployments and embedding dimension.
6. Build the Docker image with `docker build -t enterprise-ai-engineering:local engineering` and deploy to Container Apps via an authenticated CI/CD identity.
7. Run health/readiness, authenticated smoke tests and quality evaluation on every deployment; no sample user token should be committed.

Production readiness blockers: infrastructure provisioning, secrets/identity ownership, data classification, Postgres migration strategy, network policy, integration tests with live Azure services, rate limits, secure metrics scrape, availability and DR exercises, observability exporter configuration, and independent penetration/security testing.

Official guides:
- https://learn.microsoft.com/en-us/azure/developer/ai/get-started-securing-your-ai-app
- https://learn.microsoft.com/en-us/azure/search/hybrid-search-how-to-query
- https://learn.microsoft.com/en-us/azure/container-apps/overview
- https://learn.microsoft.com/en-us/entra/identity-platform/access-tokens
