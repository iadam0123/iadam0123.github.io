"""Durable, human-governed agent orchestration. External execution deliberately allowlisted and non-destructive."""
from __future__ import annotations
import json
import uuid
from typing import Annotated, Literal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from .core import Principal, authenticate, require_role, db_session, Task, AuditEvent
from .knowledge import answer_question

router=APIRouter(prefix="/api/agent",tags=["agent"])
class Proposal(BaseModel):
    action:Literal["policy_lookup","procurement_review"]
    description:str=Field(min_length=8,max_length=1200)
    amount_usd:float=Field(default=0,ge=0,le=10000000)
class Decision(BaseModel):
    approve:bool

def record(db:Session, task:Task, kind:str,actor:str,detail:str):
    db.add(AuditEvent(task_id=task.id,event_type=kind,actor=actor,detail=detail))

def view(t:Task):
    return {"id":t.id,"status":t.status,"action":t.action,"requester":t.requester,"reviewer":t.reviewer}

@router.post("/proposals")
def propose(body:Proposal,p:Annotated[Principal,Depends(require_role("Agent.Requester"))],db:Annotated[Session,Depends(db_session)]):
    if body.action=="procurement_review" and body.amount_usd>10000:
        raise HTTPException(422,"Policy limit $10,000 exceeded. No execution authorized.")
    if body.action=="policy_lookup" and body.amount_usd:
        raise HTTPException(422,"Policy lookup does not accept spending.")
    if any(x in body.description.lower() for x in ["bypass approval","ignore policy","disable audit"]):
        raise HTTPException(422,"Request cannot bypass approval policy.")
    t=Task(id=str(uuid.uuid4()),tenant=p.tenant,requester=p.subject,action=body.action,payload=body.model_dump_json(),status="PENDING_APPROVAL")
    db.add(t)
    record(db,t,"PROPOSED",p.subject,"Awaiting reviewer authorization")
    db.commit()
    return view(t)

@router.post("/proposals/{task_id}/decision")
def decide(task_id:str,body:Decision,p:Annotated[Principal,Depends(require_role("Agent.Approver"))],db:Annotated[Session,Depends(db_session)]):
    # DB transaction serializes updates of the same task in PostgreSQL.
    t=db.execute(select(Task).where(Task.id==task_id,Task.tenant==p.tenant).with_for_update()).scalar_one_or_none()
    if not t: raise HTTPException(404,"Task not found")
    if t.status!="PENDING_APPROVAL": raise HTTPException(409,"Decision already recorded")
    if t.requester==p.subject: raise HTTPException(403,"Four-eyes rule: requester cannot approve own task")
    t.reviewer=p.subject
    t.status="APPROVED" if body.approve else "REJECTED"
    record(db,t,t.status,p.subject,"Human approval decision")
    db.commit()
    return view(t)

@router.post("/proposals/{task_id}/execute")
def execute(task_id:str,p:Annotated[Principal,Depends(require_role("Agent.Executor"))],db:Annotated[Session,Depends(db_session)]):
    t=db.execute(select(Task).where(Task.id==task_id,Task.tenant==p.tenant).with_for_update()).scalar_one_or_none()
    if not t: raise HTTPException(404,"Task not found")
    if t.status!="APPROVED": raise HTTPException(409,"Approved status required; repeated execution prohibited")
    payload=json.loads(t.payload)
    # This sample tool allowlist is non-destructive; a future real procurement connector
    # would require external idempotency keys, reconciliation and outbox patterns.
    t.status="EXECUTING"
    record(db,t,"EXECUTION_STARTED",p.subject,"Allowed tool "+t.action)
    if t.action=="policy_lookup":
        try:
            result=answer_question(payload["description"],Principal(subject=t.requester,tenant=t.tenant,roles=["Knowledge.Reader"]),3)
            outcome=result.model_dump()
        except Exception:
            t.status="FAILED"
            record(db,t,"EXECUTION_FAILED",p.subject,"Lookup provider unavailable")
            db.commit()
            raise HTTPException(503,"Lookup provider unavailable")
    else:
        outcome={"status":"review_completed","disbursement":"none","amount_usd":payload["amount_usd"],"note":"No payment or external procurement execution performed."}
    t.status="COMPLETED"
    record(db,t,"EXECUTION_COMPLETED",p.subject,json.dumps(outcome)[:5000])
    db.commit()
    return {"task":view(t),"result":outcome}

@router.get("/proposals/{task_id}")
def get_task(task_id:str,p:Annotated[Principal,Depends(authenticate)],db:Annotated[Session,Depends(db_session)]):
    t=db.execute(select(Task).where(Task.id==task_id,Task.tenant==p.tenant)).scalar_one_or_none()
    if not t: raise HTTPException(404,"Task not found")
    if p.subject!=t.requester and not ({"Agent.Approver","Agent.Executor"} & set(p.roles)):
        raise HTTPException(403,"No permission to view task")
    events=db.execute(select(AuditEvent).where(AuditEvent.task_id==task_id).order_by(AuditEvent.id)).scalars().all()
    return {"task":view(t),"events":[{"event":e.event_type,"actor":e.actor,"detail":e.detail,"at":e.created_at.isoformat()} for e in events]}
