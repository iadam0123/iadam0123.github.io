import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app import core

@pytest.fixture
def harness():
    engine=create_engine("sqlite://",connect_args={"check_same_thread":False},poolclass=StaticPool)
    core.Base.metadata.create_all(engine)
    dbmaker=sessionmaker(bind=engine,expire_on_commit=False)
    current={"subject":"alice","tenant":"tenant-A","roles":["Knowledge.Reader","Agent.Requester","Governance.Assessor"]}
    def principal():
        return core.Principal(**current)
    def db():
        with dbmaker() as session: yield session
    app.dependency_overrides[core.authenticate]=principal
    app.dependency_overrides[core.db_session]=db
    with TestClient(app) as client:
        yield client,current
    app.dependency_overrides.clear()
    engine.dispose()
