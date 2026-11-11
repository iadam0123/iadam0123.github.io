"""Persisted, transparent AI assessment and minimum-control evidence."""
from __future__ import annotations
import json
import uuid
from typing import Annotated, Literal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from .core import Assessment, Principal, db_session, require_role

router=APIRouter(prefix="/api/governance",tags=["governance"])
class RiskInput(BaseModel):
    system_name:str=Field(min_length=3,max_length=200)
    sensitivity:int=Field(ge=1,le=3)
    autonomy:int=Field(ge=1,le=3)
    impact:int=Field(ge=1,le=3)
    use_case:Literal["knowledge","agent","decision_support"]

def evaluate(body:RiskInput):
    score=round(100*(.32*body.sensitivity+.38*body.autonomy+.30*body.impact)/3)
    tier="HIGH" if score>=75 else "MODERATE" if score>=50 else "LOW"
    controls=["Named owner and purpose","Data scope and authorization","Model evaluation and red-team tests",
        "Incident response and observability","Traceable human accountability"]
    if body.sensitivity>=2: controls.append("Privacy and retention assessment")
    if body.autonomy>=2: controls.append("Separate reviewer approval for side-effecting tools")
    if body.autonomy==3: controls.append("Hold unsupervised external effects pending formal exception")
    if body.impact==3: controls.append("Independent high-impact assessment and governance approval")
    return {"score":score,"tier":tier,"decision":"HOLD_FOR_REVIEW" if tier=="HIGH" else "CONDITIONAL_REVIEW",
        "controls":controls,"formula":"100*(0.32*sensitivity+0.38*autonomy+0.30*impact)/3",
        "methodology":"Illustrative internal triage heuristic; not NIST or ISO attestation."}

@router.post("/assessments")
def assess(body:RiskInput,p:Annotated[Principal,Depends(require_role("Governance.Assessor"))],db:Annotated[Session,Depends(db_session)]):
    result=evaluate(body)
    identifier=str(uuid.uuid4())
    db.add(Assessment(id=identifier,tenant=p.tenant,owner=p.subject,system_name=body.system_name,score=result["score"],tier=result["tier"],
        evidence=json.dumps({"request":body.model_dump(),"result":result})))
    db.commit()
    return {"id":identifier,**result}

@router.get("/assessments/{identifier}")
def evidence(identifier:str,p:Annotated[Principal,Depends(require_role("Governance.Assessor"))],db:Annotated[Session,Depends(db_session)]):
    record=db.execute(select(Assessment).where(Assessment.id==identifier,Assessment.tenant==p.tenant)).scalar_one_or_none()
    if not record: raise HTTPException(404,"Assessment not found")
    return {"id":record.id,"owner":record.owner,**json.loads(record.evidence)}
