"""Reproducible evaluation over deployed authenticated RAG API.

Requires TEST_API_BASE_URL and TEST_ENTRA_TOKEN (never commit tokens).
dataset JSONL: {"question":"...","must_cite":true,"required_terms":["..."]}
Writes non-secret summary; fails if below configured grounded-answer rate.
"""
from __future__ import annotations
import json, os, pathlib, sys
import httpx

base=os.environ.get("TEST_API_BASE_URL")
token=os.environ.get("TEST_ENTRA_TOKEN")
if not base or not token:
    sys.exit("Set TEST_API_BASE_URL and TEST_ENTRA_TOKEN to evaluate a real Azure deployment.")
dataset=pathlib.Path(__file__).with_name("rag_cases.jsonl")
cases=[json.loads(line) for line in dataset.read_text().splitlines() if line.strip()]
out=[]
with httpx.Client(timeout=60) as http:
    for case in cases:
        r=http.post(base.rstrip("/")+"/api/knowledge/ask",
          headers={"Authorization":"Bearer "+token},json={"question":case["question"]})
        r.raise_for_status()
        answer=r.json()
        citation_ok=bool(answer.get("citations")) if case.get("must_cite",True) else True
        grounded=all(word.lower() in answer.get("answer","").lower() for word in case.get("required_terms",[]))
        out.append({"question":case["question"],"citation_ok":citation_ok,"term_match":grounded,
            "passed":citation_ok and grounded})
rate=sum(x["passed"] for x in out)/len(out)
print(json.dumps({"sample_count":len(out),"pass_rate":rate,"results":out},indent=2))
if rate<float(os.getenv("MIN_RAG_EVAL_PASS_RATE","0.8")): sys.exit(1)
