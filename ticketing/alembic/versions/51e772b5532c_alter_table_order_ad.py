"""alter table Order add column channel

Revision ID: 51e772b5532c
Revises: 422f1f94e3
Create Date: 2013-01-11 16:19:12.346228

"""

# revision identifiers, used by Alembic.
revision = '51e772b5532c'
down_revision = '422f1f94e3'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column(u'Cart', sa.Column('channel', sa.Integer, nullable=True))
    op.add_column(u'Cart', sa.Column('operator_id', Identifier, nullable=True))
    op.create_foreign_key('Cart_ibfk_7', 'Cart', 'Operator', ['operator_id'], ['id'])
    op.add_column(u'Order', sa.Column('channel', sa.Integer, nullable=True))
    op.add_column(u'Order', sa.Column('operator_id', Identifier, nullable=True))
    op.create_foreign_key('Order_ibfk_6', 'Order', 'Operator', ['operator_id'], ['id'])

def downgrade():
    op.drop_constraint('Order_ibfk_6', 'Order', 'foreignkey')
    op.drop_column(u'Order', 'operator_id')
    op.drop_column(u'Order', 'channel')
    op.drop_constraint('Cart_ibfk_7', 'Cart', 'foreignkey')
    op.drop_column(u'Cart', 'operator_id')
    op.drop_column(u'Cart', 'channel')
