"""Add performance indexes.

Revision ID: 002_add_performance_indexes
Revises: d943cf442dc4
Create Date: 2025-10-20 12:00:00.000000

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "002_add_performance_indexes"
down_revision = "d943cf442dc4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add performance indexes for frequently queried columns."""
    # Index on journal_entries.created_at for sorting and date range queries
    op.create_index(
        "ix_journal_entries_created_at",
        "journal_entries",
        ["created_at"],
        unique=False,
    )

    # Index on conversations.created_at for sorting
    op.create_index(
        "ix_conversations_created_at",
        "conversations",
        ["created_at"],
        unique=False,
    )

    # Composite index on journal_entries (user_id, created_at) for efficient user queries
    op.create_index(
        "ix_journal_entries_user_created",
        "journal_entries",
        ["user_id", "created_at"],
        unique=False,
    )

    # Composite index on conversations (user_id, created_at) for efficient user queries
    op.create_index(
        "ix_conversations_user_created",
        "conversations",
        ["user_id", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    """Remove performance indexes."""
    op.drop_index("ix_conversations_user_created", table_name="conversations")
    op.drop_index("ix_journal_entries_user_created", table_name="journal_entries")
    op.drop_index("ix_conversations_created_at", table_name="conversations")
    op.drop_index("ix_journal_entries_created_at", table_name="journal_entries")
