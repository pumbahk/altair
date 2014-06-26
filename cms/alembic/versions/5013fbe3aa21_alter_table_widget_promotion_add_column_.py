"""alter table widget_promotion add column use_newstyle

Revision ID: 5013fbe3aa21
Revises: d49d1b04a0c
Create Date: 2014-06-09 18:17:55.370686

"""

# revision identifiers, used by Alembic.
revision = '5013fbe3aa21'
down_revision = 'd49d1b04a0c'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text


def upgrade():
    op.add_column('widget_promotion', sa.Column('use_newstyle', sa.Boolean(), nullable=False,default=False, server_default=text('0')))

def downgrade():
    op.drop_column('widget_promotion', 'use_newstyle')
