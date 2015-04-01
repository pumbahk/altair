"""alter table EventSetting add column visible

Revision ID: 479dfa5c0001
Revises: 248521a3b5b8
Create Date: 2015-03-27 15:33:37.757222

"""

# revision identifiers, used by Alembic.
revision = '479dfa5c0001'
down_revision = '248521a3b5b8'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('EventSetting', sa.Column('visible', sa.Boolean(), nullable=False,default=True, server_default=text('1')))

def downgrade():
    op.drop_column(u'EventSetting', u'visible')
