"""create host model

Revision ID: 57feb087d5c7
Revises: 43c6379bbc86
Create Date: 2012-11-06 14:12:22.266121

"""

# revision identifiers, used by Alembic.
revision = '57feb087d5c7'
down_revision = '43c6379bbc86'

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table('host',
                    sa.Column('organization_id', sa.Integer(), nullable=True),
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('host_name', sa.Unicode(length=255), nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('host_name')
                    )

def downgrade():
    op.drop_table('host')
