"""performance has code

Revision ID: 2af18a487a43
Revises: 2454d633fbc5
Create Date: 2013-03-22 10:07:46.184625

"""

# revision identifiers, used by Alembic.
revision = '2af18a487a43'
down_revision = '2454d633fbc5'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    op.add_column('performance', sa.Column('code', sa.String(length=12), nullable=True))

def downgrade():
    op.drop_column('performance', 'code')
