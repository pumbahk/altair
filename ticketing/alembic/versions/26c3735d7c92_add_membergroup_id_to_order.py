"""add_membergroup_id_to_order_and_cart

Revision ID: 26c3735d7c92
Revises: 2a2157bc2913
Create Date: 2015-10-30 10:40:44.535675

"""

# revision identifiers, used by Alembic.
revision = '26c3735d7c92'
down_revision = '2a2157bc2913'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('Order', sa.Column('membergroup_id', Identifier, sa.ForeignKey('MemberGroup.id', name='Order_ibfk_10'), nullable=True))
    op.add_column('Cart', sa.Column('membergroup_id', Identifier, sa.ForeignKey('MemberGroup.id', name='Cart_ibfk_10'), nullable=True))
    op.execute('UPDATE `Order` JOIN `Member` ON `Order`.user_id=`Member`.user_id SET `Order`.membergroup_id=`Member`.membergroup_id WHERE `Member`.deleted_at IS NULL;')
    op.execute('UPDATE `Cart` JOIN `Order` ON `Cart`.order_id=`Order`.id JOIN `Member` ON `Order`.user_id=`Member`.user_id SET `Cart`.membergroup_id=`Member`.membergroup_id WHERE `Member`.deleted_at IS NULL;')

def downgrade():
    op.drop_constraint('Cart', 'Cart_ibfk_10', type_='foreignkey')
    op.drop_column('Cart', 'membergroup_id')
    op.drop_constraint('Order', 'Order_ibfk_10', type_='foreignkey')
    op.drop_column('Order', 'membergroup_id')
