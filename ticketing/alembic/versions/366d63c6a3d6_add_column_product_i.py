"""add column product_item_id on SejTicket

Revision ID: 366d63c6a3d6
Revises: 43e67786c152
Create Date: 2013-08-28 20:39:24.827223

"""

# revision identifiers, used by Alembic.
revision = '366d63c6a3d6'
down_revision = '43e67786c152'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('SejTicket', sa.Column('product_item_id', Identifier(), sa.ForeignKey('ProductItem.id', name='SejTicket_ibfk_2'), nullable=True))

def downgrade():
    op.drop_constraint(u'SejTicket_ibfk_2', u'SejTicket', type_="foreignkey")
    op.drop_column(u'SejTicket', 'product_item_id')
