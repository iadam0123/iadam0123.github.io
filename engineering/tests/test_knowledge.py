from types import SimpleNamespace
from app import knowledge

def test_knowledge_answer_restricts_citation_to_retrieved_passages(monkeypatch):
    class FakeResponses:
        def create(self,**kwargs):
            return SimpleNamespace(output_text="Deployment requires review [DOC-1]. An invalid citation [DOC-99] is ignored.")
    class FakeClient: responses=FakeResponses()
    monkeypatch.setattr(knowledge,"retrieve",lambda q,p,k:[{"title":"AI review","content":"Review required.","source":"synthetic://review"}])
    monkeypatch.setattr(knowledge,"llm_client",lambda:FakeClient())
    monkeypatch.setenv("AZURE_OPENAI_CHAT_DEPLOYMENT","test-deployment")
    p=knowledge.Principal(subject="alice",tenant="tenant-A",roles=["Knowledge.Reader"])
    answer=knowledge.answer_question("How to deploy AI?",p)
    assert len(answer.citations)==1
    assert answer.citations[0].ref=="DOC-1"
    assert answer.citations[0].source=="synthetic://review"

def test_empty_retrieval_abstains(monkeypatch):
    monkeypatch.setattr(knowledge,"retrieve",lambda q,p,k:[])
    p=knowledge.Principal(subject="alice",tenant="tenant-A",roles=["Knowledge.Reader"])
    answer=knowledge.answer_question("unknown",p)
    assert not answer.grounded and not answer.citations

def test_api_rejects_without_knowledge_role(harness):
    client,current=harness
    current["roles"]=[]
    assert client.post("/api/knowledge/ask",json={"question":"Tell me about policy"}).status_code==403
