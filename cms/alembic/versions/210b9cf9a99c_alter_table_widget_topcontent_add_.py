"""alter table widget_topcontent add column use_newstyle

Revision ID: 210b9cf9a99c
Revises: 2dfa824a5c35
Create Date: 2014-06-17 11:07:16.153212

"""

# revision identifiers, used by Alembic.
revision = '210b9cf9a99c'
down_revision = '2dfa824a5c35'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text

def upgrade():
    op.add_column('widget_topcontent', sa.Column('use_newstyle', sa.Boolean(), nullable=False,default=False, server_default=text('0')))

def downgrade():
    op.drop_column('widget_topcontent', 'use_newstyle')
