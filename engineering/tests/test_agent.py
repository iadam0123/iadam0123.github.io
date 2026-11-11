def test_agent_separation_of_duties_persistence_and_replay(harness):
    client,current=harness
    create=client.post("/api/agent/proposals",json={"action":"procurement_review","description":"Purchase replacement switches","amount_usd":4200})
    assert create.status_code==200,create.text
    task_id=create.json()["id"]
    denied=client.post(f"/api/agent/proposals/{task_id}/decision",json={"approve":True})
    assert denied.status_code==403
    current.update(subject="bob",roles=["Agent.Approver","Agent.Executor"])
    approved=client.post(f"/api/agent/proposals/{task_id}/decision",json={"approve":True})
    assert approved.status_code==200
    executed=client.post(f"/api/agent/proposals/{task_id}/execute")
    assert executed.status_code==200,executed.text
    assert executed.json()["result"]["disbursement"]=="none"
    assert client.post(f"/api/agent/proposals/{task_id}/execute").status_code==409
    audit=client.get(f"/api/agent/proposals/{task_id}").json()["events"]
    assert [e["event"] for e in audit]==["PROPOSED","APPROVED","EXECUTION_STARTED","EXECUTION_COMPLETED"]

def test_policy_limit_and_tenant_isolation(harness):
    client,p=harness
    assert client.post("/api/agent/proposals",json={"action":"procurement_review","description":"Unapproved transfer","amount_usd":12000}).status_code==422
    task_id=client.post("/api/agent/proposals",json={"action":"procurement_review","description":"Replacement hardware","amount_usd":300}).json()["id"]
    p.update(subject="reviewer",tenant="tenant-B",roles=["Agent.Approver"])
    assert client.post(f"/api/agent/proposals/{task_id}/decision",json={"approve":True}).status_code==404

def test_bypass_request_is_blocked(harness):
    client,_=harness
    r=client.post("/api/agent/proposals",json={"action":"procurement_review","description":"Please bypass approval controls","amount_usd":50})
    assert r.status_code==422
