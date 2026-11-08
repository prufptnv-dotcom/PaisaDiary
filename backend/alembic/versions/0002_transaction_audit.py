"""Transaction audit trail and reversal metadata.

Revision ID: 0002_transaction_audit
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_transaction_audit"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "transactions",
        sa.Column("is_reversed", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "transactions",
        sa.Column(
            "reversal_of_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("transactions.id", ondelete="RESTRICT"),
            nullable=True,
        ),
    )
    op.create_index("ix_transactions_reversal_of_id", "transactions", ["reversal_of_id"], unique=True)

    op.create_table(
        "transaction_audits",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("transaction_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("transactions.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("event_type", sa.String(24), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("before_snapshot", sa.JSON(), nullable=True),
        sa.Column("after_snapshot", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_transaction_audits_user_id", "transaction_audits", ["user_id"])
    op.create_index("ix_transaction_audits_transaction_id", "transaction_audits", ["transaction_id"])
    op.create_index("ix_transaction_audits_user_created", "transaction_audits", ["user_id", "created_at"])
    op.create_index("ix_transaction_audits_transaction_created", "transaction_audits", ["transaction_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_transaction_audits_transaction_created", table_name="transaction_audits")
    op.drop_index("ix_transaction_audits_user_created", table_name="transaction_audits")
    op.drop_index("ix_transaction_audits_transaction_id", table_name="transaction_audits")
    op.drop_index("ix_transaction_audits_user_id", table_name="transaction_audits")
    op.drop_table("transaction_audits")
    op.drop_index("ix_transactions_reversal_of_id", table_name="transactions")
    op.drop_column("transactions", "reversal_of_id")
    op.drop_column("transactions", "is_reversed")
