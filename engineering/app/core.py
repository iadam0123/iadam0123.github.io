"""Shared identities, authorization and durable database primitives."""
from __future__ import annotations
import os
from datetime import datetime, timezone
from functools import lru_cache
from typing import Annotated
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, String, DateTime, Text, Integer, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, Session
import jwt
from jwt import PyJWKClient

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./engineering.db")
if DATABASE_URL.startswith("sqlite") and os.getenv("ENVIRONMENT", "development") == "production":
    raise RuntimeError("Production requires a durable PostgreSQL DATABASE_URL.")
engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

class Base(DeclarativeBase): pass
def utcnow(): return datetime.now(timezone.utc)
class Task(Base):
    __tablename__ = "agent_tasks"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant: Mapped[str] = mapped_column(String(100), index=True)
    requester: Mapped[str] = mapped_column(String(200))
    action: Mapped[str] = mapped_column(String(100))
    payload: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default="PENDING_APPROVAL")
    reviewer: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
class AuditEvent(Base):
    __tablename__ = "audit_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[str] = mapped_column(String(36), ForeignKey("agent_tasks.id"))
    event_type: Mapped[str] = mapped_column(String(50))
    actor: Mapped[str] = mapped_column(String(200))
    detail: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
class Assessment(Base):
    __tablename__ = "ai_assessments"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant: Mapped[str] = mapped_column(String(100), index=True)
    owner: Mapped[str] = mapped_column(String(200))
    system_name: Mapped[str] = mapped_column(String(200))
    score: Mapped[int] = mapped_column(Integer)
    tier: Mapped[str] = mapped_column(String(20))
    evidence: Mapped[str] = mapped_column(Text)

def db_session():
    with SessionLocal() as session: yield session

class Principal(BaseModel):
    subject: str
    tenant: str
    roles: list[str] = Field(default_factory=list)

bearer = HTTPBearer(auto_error=False)
@lru_cache
def jwks_client(tenant: str):
    return PyJWKClient("https://login.microsoftonline.com/" + tenant + "/discovery/v2.0/keys")

def authenticate(credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]) -> Principal:
    tenant = os.getenv("ENTRA_TENANT_ID")
    audience = os.getenv("ENTRA_API_AUDIENCE")
    if not tenant or not audience:
        raise HTTPException(503, "Microsoft Entra ID authentication is not configured.")
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(401, "Bearer token required.", headers={"WWW-Authenticate": "Bearer"})
    token = credentials.credentials
    try:
        key = jwks_client(tenant).get_signing_key_from_jwt(token).key
        claims = jwt.decode(token, key, algorithms=["RS256"], audience=audience, issuer="https://login.microsoftonline.com/" + tenant + "/v2.0", options={"require":["exp","iat","iss","aud","tid","sub"]}, leeway=30)
        if claims["tid"] != tenant: raise ValueError("Tenant claim mismatch.")
        roles = claims.get("roles", [])
        if not isinstance(roles, list): raise ValueError("Invalid roles.")
        return Principal(subject=claims.get("oid", claims["sub"]), tenant=claims["tid"], roles=roles)
    except (jwt.PyJWTError, ValueError, Exception) as exc:
        # No token contents or exception details are logged.
        raise HTTPException(401, "Invalid identity token.") from None

def require_role(name: str):
    def verify(p: Annotated[Principal, Depends(authenticate)]):
        if name not in p.roles: raise HTTPException(403, "Insufficient application role.")
        return p
    return verify
