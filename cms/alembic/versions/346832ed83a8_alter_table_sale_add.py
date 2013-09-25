"""alter table sale add column publicp

Revision ID: 346832ed83a8
Revises: 2b784eb107d2
Create Date: 2013-09-20 16:04:44.342214

"""

# revision identifiers, used by Alembic.
revision = '346832ed83a8'
down_revision = '2b784eb107d2'

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('sale', sa.Column('publicp', sa.Boolean(), nullable=False, default=True))
    op.execute('UPDATE sale SET publicp = 1;')

def downgrade():
    op.drop_column('sale', 'publicp')
