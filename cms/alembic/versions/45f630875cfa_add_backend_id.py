"""add backend id

Revision ID: 45f630875cfa
Revises: 54857843f0b6
Create Date: 2012-05-25 11:10:44.892498

"""

# revision identifiers, used by Alembic.
revision = '45f630875cfa'
down_revision = '54857843f0b6'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column("performance", "backend_performance_id", existing_type=sa.Integer, name="backend_id")
    op.add_column("event", sa.Column("backend_id", sa.Integer))

def downgrade():
    op.alter_column("performance", "backend_id", existing_type=sa.Integer, name="backend_performance_id")
    op.drop_column("event", "backend_id")

