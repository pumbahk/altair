"""alter table widget_topic add column enable_newstyle

Revision ID: 2dfa824a5c35
Revises: 5013fbe3aa21
Create Date: 2014-06-16 14:53:41.937382

"""

# revision identifiers, used by Alembic.
revision = '2dfa824a5c35'
down_revision = '5013fbe3aa21'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text


def upgrade():
    op.add_column('widget_topic', sa.Column('use_newstyle', sa.Boolean(), nullable=False,default=False, server_default=text('0')))

def downgrade():
    op.drop_column('widget_topic', 'use_newstyle')
