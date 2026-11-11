from app.governance import RiskInput,evaluate

def test_deterministic_risk_and_persisted_evidence(harness):
    client,_=harness
    body={"system_name":"Supplier AI","sensitivity":3,"autonomy":3,"impact":3,"use_case":"agent"}
    response=client.post("/api/governance/assessments",json=body)
    assert response.status_code==200,response.text
    data=response.json()
    assert data["score"]==100 and data["tier"]=="HIGH"
    evidence=client.get("/api/governance/assessments/"+data["id"])
    assert evidence.status_code==200
    assert evidence.json()["result"]["decision"]=="HOLD_FOR_REVIEW"

def test_tenant_boundary(harness):
    client,current=harness
    response=client.post("/api/governance/assessments",json={"system_name":"Knowledge AI","sensitivity":1,"autonomy":1,"impact":1,"use_case":"knowledge"})
    current["tenant"]="tenant-B"
    assert client.get("/api/governance/assessments/"+response.json()["id"]).status_code==404

def test_low_risk_score():
    assert evaluate(RiskInput(system_name="demo",sensitivity=1,autonomy=1,impact=1,use_case="knowledge"))["score"]==33
