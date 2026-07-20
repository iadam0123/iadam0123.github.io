const systems=[
 {n:"Enterprise Architecture",r:"adam-architecture-diagram",c:"platform",m:"Implemented portfolio system",d:"Capability, platform, control and transition architectures in one inspectable map."},
 {n:"AI Governance Command Center",r:"ai-governance-command-center",c:"ai",m:"Production-ready implementation",d:"AI inventory, risk classification, approvals, controls, evidence and lifecycle governance."},
 {n:"Governed AI Software Factory",r:"software-factory-architecture",c:"platform",m:"Production-ready reference",d:"AI-assisted delivery with human gates, supply-chain integrity and operating telemetry."},
 {n:"AI SOC Sentinel",r:"ai-soc-sentinel",c:"security",m:"Production-ready reference",d:"Grounded investigation assistance, detection engineering and controlled response."},
 {n:"Secure Agentic AI Platform",r:"secure-agentic-ai-platform",c:"ai",m:"Implementation planned",d:"Agent identity, tool authorization, memory, policy, isolation and accountable autonomy."},
 {n:"AI Security Architecture",r:"ai-security-reference-architecture",c:"security",m:"Implementation planned",d:"Threat-driven controls across models, data, prompts, agents, APIs and infrastructure."},
 {n:"Responsible AI Governance",r:"responsible-ai-governance-framework",c:"ai",m:"Implementation planned",d:"A practical governance framework aligning risk, value, accountability and assurance."},
 {n:"Enterprise LLMOps",r:"enterprise-llmops-platform",c:"ai",m:"Implementation planned",d:"Model gateway, evaluation, release, monitoring, drift, safety and cost governance."},
 {n:"AI Red Team Evaluation",r:"ai-red-team-evaluation-platform",c:"security",m:"Implementation planned",d:"Repeatable adversarial testing for prompt, retrieval, model and agent attack surfaces."},
 {n:"AI SDLC Security",r:"ai-sdlc-security-platform",c:"security",m:"Implementation planned",d:"SAST, DAST, SCA, API, IaC and AI-assisted remediation embedded in delivery."},
 {n:"Zero Trust Enterprise",r:"zero-trust-enterprise-architecture",c:"security",m:"Implementation planned",d:"Continuous verification across workforce, workloads, agents, networks and data."},
 {n:"Cloud Detection & Response",r:"cloud-detection-response-engineering",c:"security",m:"Implementation planned",d:"Cross-cloud telemetry, detection as code, triage, response and control validation."},
 {n:"Secure AI Banking Assistant",r:"secure-ai-banking-assistant",c:"industry",m:"Reference implementation",d:"Explainable, approval-gated financial workflows with data and conduct controls."},
 {n:"Healthcare AI Security",r:"healthcare-ai-security-platform",c:"industry",m:"Reference implementation",d:"Synthetic-data clinical assistance with privacy, safety and access safeguards."},
 {n:"Federal Zero Trust AI",r:"federal-zero-trust-ai-platform",c:"industry",m:"Reference implementation",d:"Government-oriented AI controls, identity, evidence and secure operating patterns."},
 {n:"Energy AI Operations",r:"energy-infrastructure-ai-operations",c:"industry",m:"Reference implementation",d:"AI-assisted reliability and cyber operations for critical energy infrastructure."},
 {n:"Architecture Evidence Registry",r:"architecture-evidence-registry",c:"evidence",m:"Assurance system",d:"The central record connecting every claim to code, tests, deployments and telemetry."},
 {n:"Security Control Validation",r:"security-control-validation",c:"evidence",m:"Assurance system",d:"Executable checks proving whether documented controls are present and effective."},
 {n:"Performance & Resilience",r:"performance-resilience-benchmarks",c:"evidence",m:"Assurance system",d:"Load, scale, failure, recovery and continuity evidence across portfolio systems."},
 {n:"Enterprise Runbooks",r:"enterprise-runbooks-playbooks",c:"evidence",m:"Operational system",d:"Deployment, incident, rollback, recovery and escalation procedures as code."}
];
const grid=document.querySelector("#systems-grid");
function render(filter="all"){
 grid.innerHTML=systems.filter(s=>filter==="all"||s.c===filter).map(s=>`<article class="system-card"><div class="meta"><span>${s.c}</span><span>${s.m}</span></div><h3>${s.n}</h3><p>${s.d}</p><a href="https://iadam0123.github.io/${s.r}/">Explore system →</a></article>`).join("");
}
document.querySelectorAll(".filter").forEach(b=>b.addEventListener("click",()=>{document.querySelector(".filter.active")?.classList.remove("active");b.classList.add("active");render(b.dataset.filter)}));
render();
