"""alter table performance add column public

Revision ID: 142cf4285441
Revises: 3e3380981e30
Create Date: 2013-06-12 19:14:54.692943

"""

# revision identifiers, used by Alembic.
revision = '142cf4285441'
down_revision = '3e3380981e30'

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('performance', sa.Column('public', sa.Boolean, nullable=False, default=True))
    op.execute("update performance set public = 1;")

def downgrade():
    op.drop_column('performance', 'public')