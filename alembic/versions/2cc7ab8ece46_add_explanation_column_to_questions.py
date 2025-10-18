"""Add explanation column to questions

Revision ID: add_explanation_column
Revises: 
Create Date: 2025-10-18 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_explanation_column'
down_revision = None  # replace with the previous revision ID if you have one
branch_labels = None
depends_on = None


def upgrade():
    # Add 'explanation' column to 'questions' table
    op.add_column('questions', sa.Column('explanation', sa.Text, nullable=True))


def downgrade():
    # Remove 'explanation' column if downgrading
    op.drop_column('questions', 'explanation')
