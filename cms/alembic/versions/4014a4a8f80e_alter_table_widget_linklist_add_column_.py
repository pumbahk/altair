"""alter table widget_linklist add column use_newstyle

Revision ID: 4014a4a8f80e
Revises: 210b9cf9a99c
Create Date: 2014-06-18 17:32:09.292609

"""

# revision identifiers, used by Alembic.
revision = '4014a4a8f80e'
down_revision = '210b9cf9a99c'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text

def upgrade():
    op.add_column('widget_linklist', sa.Column('use_newstyle', sa.Boolean(), nullable=False,default=False, server_default=text('0')))

def downgrade():
    op.drop_column('widget_linklist', 'use_newstyle')
