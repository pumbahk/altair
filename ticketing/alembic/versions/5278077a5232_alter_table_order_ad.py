"""alter table Order add column refund_id

Revision ID: 5278077a5232
Revises: 368e33588cbe
Create Date: 2013-02-14 11:35:43.306963

"""

# revision identifiers, used by Alembic.
revision = '5278077a5232'
down_revision = '368e33588cbe'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('Order', sa.Column('refund_id', Identifier()))
    op.create_foreign_key('Order_ibfk_7', 'Order', 'Refund', ['refund_id'], ['id'])
    op.drop_table('Refund_Order')

def downgrade():
    op.create_table('Refund_Order',
        sa.Column('refund_id', Identifier, nullable=False),
        sa.Column('order_no', sa.String(255), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['refund_id'], ['Refund.id'], 'Refund_Order_ibfk_1', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['order_no'], ['Order.order_no'], 'Refund_Order_ibfk_2', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('refund_id', 'order_no')
        )
    op.drop_constraint(u'Order_ibfk_7', 'Order', type="foreignkey")
    op.drop_column('Order', 'refund_id')
