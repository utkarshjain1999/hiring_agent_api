"""add round columns

Revision ID: add_round_columns
Revises: 1a2b3c4d5e6f
Create Date: 2024-03-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_round_columns'
down_revision = '1a2b3c4d5e6f'  # Replace with your last migration ID
branch_labels = None
depends_on = None

def upgrade():
    # Add round columns to job_descriptions table
    op.add_column('job_descriptions', sa.Column('round1', sa.Text(), nullable=True))
    op.add_column('job_descriptions', sa.Column('round2', sa.Text(), nullable=True))
    op.add_column('job_descriptions', sa.Column('round3', sa.Text(), nullable=True))
    op.add_column('job_descriptions', sa.Column('round4', sa.Text(), nullable=True))
    op.add_column('job_descriptions', sa.Column('round5', sa.Text(), nullable=True))

def downgrade():
    # Remove round columns from job_descriptions table
    op.drop_column('job_descriptions', 'round1')
    op.drop_column('job_descriptions', 'round2')
    op.drop_column('job_descriptions', 'round3')
    op.drop_column('job_descriptions', 'round4')
    op.drop_column('job_descriptions', 'round5') 