"""Create durable task, audit, and governance tables.

Revision ID: 0001_initial
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision="0001_initial"
down_revision=None
branch_labels=None
depends_on=None

def upgrade():
    op.create_table("agent_tasks",
        sa.Column("id",sa.String(36),primary_key=True),
        sa.Column("tenant",sa.String(100),nullable=False),
        sa.Column("requester",sa.String(200),nullable=False),
        sa.Column("action",sa.String(100),nullable=False),
        sa.Column("payload",sa.Text(),nullable=False),
        sa.Column("status",sa.String(32),nullable=False),
        sa.Column("reviewer",sa.String(200),nullable=True),
        sa.Column("created_at",sa.DateTime(timezone=True),nullable=False))
    op.create_index("ix_agent_tasks_tenant","agent_tasks",["tenant"])
    op.create_table("audit_events",
        sa.Column("id",sa.Integer(),primary_key=True,autoincrement=True),
        sa.Column("task_id",sa.String(36),sa.ForeignKey("agent_tasks.id"),nullable=False),
        sa.Column("event_type",sa.String(50),nullable=False),
        sa.Column("actor",sa.String(200),nullable=False),
        sa.Column("detail",sa.Text(),nullable=False),
        sa.Column("created_at",sa.DateTime(timezone=True),nullable=False))
    op.create_table("ai_assessments",
        sa.Column("id",sa.String(36),primary_key=True),
        sa.Column("tenant",sa.String(100),nullable=False),
        sa.Column("owner",sa.String(200),nullable=False),
        sa.Column("system_name",sa.String(200),nullable=False),
        sa.Column("score",sa.Integer(),nullable=False),
        sa.Column("tier",sa.String(20),nullable=False),
        sa.Column("evidence",sa.Text(),nullable=False))
    op.create_index("ix_ai_assessments_tenant","ai_assessments",["tenant"])
def downgrade():
    op.drop_index("ix_ai_assessments_tenant",table_name="ai_assessments")
    op.drop_table("ai_assessments")
    op.drop_table("audit_events")
    op.drop_index("ix_agent_tasks_tenant",table_name="agent_tasks")
    op.drop_table("agent_tasks")
