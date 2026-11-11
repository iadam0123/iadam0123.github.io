"""Provision a hybrid vector index and seed synthetic, role-scoped enterprise policies.

Usage: python -m scripts.seed_search
Requires Azure RBAC roles Search Service Contributor + Search Index Data Contributor
and Cognitive Services OpenAI User for embedding.
Never ingest actual customer or employee data into a public demonstration.
"""
from __future__ import annotations
import os
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents import SearchClient
from azure.search.documents.indexes.models import (
    SearchIndex, SearchField, SimpleField, SearchableField, SearchFieldDataType,
    VectorSearch, HnswAlgorithmConfiguration, VectorSearchProfile
)
from openai import OpenAI

tenant=os.environ["ENTRA_TENANT_ID"]
endpoint=os.environ["AZURE_SEARCH_ENDPOINT"]
name=os.getenv("AZURE_SEARCH_INDEX","enterprise-knowledge")
dimension=int(os.getenv("AZURE_EMBEDDING_DIMENSIONS","1536"))
credential=DefaultAzureCredential(exclude_interactive_browser_credential=True)
provider=get_bearer_token_provider(credential(),"https://cognitiveservices.azure.com/.default")
client=OpenAI(base_url=os.environ["AZURE_OPENAI_ENDPOINT"].rstrip("/")+"/openai/v1/",api_key=provider)
index=SearchIndex(
    name=name,
    fields=[
        SimpleField(name="id",type=SearchFieldDataType.String,key=True,filterable=True),
        SimpleField(name="tenant_id",type=SearchFieldDataType.String,filterable=True),
        SearchField(name="permitted_roles",type=SearchFieldDataType.Collection(SearchFieldDataType.String),filterable=True),
        SearchableField(name="title",type=SearchFieldDataType.String),
        SearchableField(name="content",type=SearchFieldDataType.String),
        SimpleField(name="source",type=SearchFieldDataType.String,filterable=False),
        SearchField(name="content_vector",type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,vector_search_dimensions=dimension,vector_search_profile_name="vector-hnsw")
    ],
    vector_search=VectorSearch(algorithms=[HnswAlgorithmConfiguration(name="hnsw")],
        profiles=[VectorSearchProfile(name="vector-hnsw",algorithm_configuration_name="hnsw")])
)
SearchIndexClient(endpoint,credential).create_or_update_index(index)
records=[
 ("demo-ai-approval","Production AI approval policy","A production AI deployment requires model quality evaluation, threat modeling, accountable sign-off, budget validation and operational monitoring.",["Knowledge.Reader"]),
 ("demo-classification","Enterprise information classification","Classify input documents before retrieval, apply least privilege security trimming, and prohibit restricted content in unapproved model contexts.",["Knowledge.Reader"]),
 ("demo-agent-controls","Agent tool execution policy","Agent tool execution requires a documented purpose, bounded authority, named requester, independent human approval and a durable audit record.",["Knowledge.Reader"]),
 ("demo-incident","Security incident playbook","Security incidents require preserving evidence, revoking compromised identities, isolating affected services and escalating to the security response team.",["Knowledge.Reader"]),
]
documents=[]
for identifier,title,body,roles in records:
    vector=client.embeddings.create(model=os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"],input=body).data[0].embedding
    if len(vector)!=dimension: raise RuntimeError("Embedding dimensionality mismatch")
    documents.append({"id":identifier,"tenant_id":tenant,"title":title,"content":body,
        "source":"synthetic://"+identifier,"permitted_roles":roles,"content_vector":vector})
results=SearchClient(endpoint,name,credential).upload_documents(documents)
if not all(r.succeeded for r in results): raise RuntimeError("One or more documents failed to index")
print("Successfully indexed",len(results),"synthetic reference documents.")
