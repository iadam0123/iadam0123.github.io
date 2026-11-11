"""Unified enterprise AI reference API: RAG, governed agents, risk evidence."""
from __future__ import annotations
import logging, os, time
from fastapi import FastAPI, Request
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from .core import Base, engine
from .knowledge import router as knowledge
from .agents import router as agents
from .governance import router as governance

logging.basicConfig(level=os.environ.get("LOG_LEVEL","INFO"))
app=FastAPI(title="Enterprise AI Architecture Evidence API",version="1.0.0",
    description="Azure-connected reference implementation. /health/live requires no credentials; all business APIs require Entra app roles.")
app.include_router(knowledge)
app.include_router(agents)
app.include_router(governance)
REQUESTS=Counter("enterprise_http_requests_total","Requests",["method","route","status"])
DURATION=Histogram("enterprise_http_duration_seconds","Request latency",["method","route"])
@app.middleware("http")
async def monitor(request:Request,call_next):
    start=time.perf_counter()
    response=await call_next(request)
    route=getattr(request.scope.get("route"),"path","unmatched")
    REQUESTS.labels(request.method,route,str(response.status_code)).inc()
    DURATION.labels(request.method,route).observe(time.perf_counter()-start)
    return response
@app.get("/health/live")
def live(): return {"status":"alive","mode":"azure-connected-when-configured"}
@app.get("/health/ready")
def ready():
    # Indicates config readiness; external service connectivity is validated by integration checks.
    required=["ENTRA_TENANT_ID","ENTRA_API_AUDIENCE","AZURE_OPENAI_ENDPOINT","AZURE_OPENAI_CHAT_DEPLOYMENT","AZURE_OPENAI_EMBEDDING_DEPLOYMENT","AZURE_SEARCH_ENDPOINT"]
    missing=[x for x in required if not os.getenv(x)]
    return {"configured":not missing,"missing":missing}
# Restrict metrics to an authenticated scrape gateway in production (otherwise disabled).
if os.getenv("ENABLE_METRICS_ENDPOINT")=="true":
    @app.get("/internal/metrics",include_in_schema=False)
    def metrics(): return Response(content=generate_latest(),media_type=CONTENT_TYPE_LATEST)
if os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING"):
    from azure.monitor.opentelemetry import configure_azure_monitor
    configure_azure_monitor(connection_string=os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"])
else:
    FastAPIInstrumentor.instrument_app(app)
@app.on_event("startup")
def initialize():
    # Production schema must be managed by migrations; set RUN_SCHEMA_CREATE=false in production.
    if os.getenv("RUN_SCHEMA_CREATE","true").lower()=="true": Base.metadata.create_all(bind=engine)
