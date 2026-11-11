from types import SimpleNamespace
from app import knowledge

def test_authorization_security_trim_passed_to_azure_search(monkeypatch):
    called={}
    class FakeEmbeddings:
        def create(self,**kwargs):return SimpleNamespace(data=[SimpleNamespace(embedding=[0.1,0.2])])
    class FakeOpenAI: embeddings=FakeEmbeddings()
    class FakeSearch:
        def search(self,**kwargs):
            called.update(kwargs)
            return [{"title":"Policy","content":"Approved content","source":"synthetic://test"}]
    monkeypatch.setattr(knowledge,"llm_client",lambda:FakeOpenAI())
    monkeypatch.setattr(knowledge,"search_client",lambda:FakeSearch())
    monkeypatch.setenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT","emb")
    p=knowledge.Principal(subject="alice",tenant="tenant-A",roles=["Knowledge.Reader"])
    docs=knowledge.retrieve("AI deployment",p,3)
    assert len(docs)==1
    assert "tenant_id eq 'tenant-A'" in called["filter"]
    assert "permitted_roles/any" in called["filter"]
    assert called["vector_filter_mode"]=="preFilter"

def test_no_role_yields_zero_documents(monkeypatch):
    p=knowledge.Principal(subject="alice",tenant="tenant-A",roles=[])
    assert knowledge.retrieve("AI deployment",p,3)==[]
