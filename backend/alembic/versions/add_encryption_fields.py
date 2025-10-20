"""Add encryption fields to users and journal_entries tables

Revision ID: e8f5a6b2c3d4
Revises: d943cf442dc4
Create Date: 2025-10-20 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e8f5a6b2c3d4'
down_revision: Union[str, Sequence[str], None] = 'd943cf442dc4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add encryption fields to users and journal_entries tables."""
    # Add encryption fields to users table
    op.add_column('users', sa.Column('encryption_salt', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('encryption_key_hash', sa.String(length=255), nullable=True))

    # Add is_encrypted field to journal_entries table
    op.add_column('journal_entries', sa.Column('is_encrypted', sa.Boolean(), nullable=False, server_default='false'))

    # Make content column nullable (was NOT NULL in initial migration)
    op.alter_column('journal_entries', 'content',
                    existing_type=sa.Text(),
                    nullable=True)

    # Add index on created_at for journal_entries (for better query performance)
    op.create_index(op.f('ix_journal_entries_created_at'), 'journal_entries', ['created_at'], unique=False)


def downgrade() -> None:
    """Remove encryption fields from users and journal_entries tables."""
    # Remove index
    op.drop_index(op.f('ix_journal_entries_created_at'), table_name='journal_entries')

    # Restore content column to NOT NULL
    op.alter_column('journal_entries', 'content',
                    existing_type=sa.Text(),
                    nullable=False)

    # Remove is_encrypted from journal_entries
    op.drop_column('journal_entries', 'is_encrypted')

    # Remove encryption fields from users
    op.drop_column('users', 'encryption_key_hash')
    op.drop_column('users', 'encryption_salt')
