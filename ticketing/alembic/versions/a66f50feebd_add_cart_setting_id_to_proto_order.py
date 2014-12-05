"""add_cart_setting_id_to_proto_order

Revision ID: a66f50feebd
Revises: 56aa0210befb
Create Date: 2014-12-05 17:18:00.551161

"""

# revision identifiers, used by Alembic.
revision = 'a66f50feebd'
down_revision = '56aa0210befb'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('ProtoOrder', sa.Column('cart_setting_id', Identifier(), sa.ForeignKey('CartSetting.id', name='ProtoOrder_ibfk_11'), nullable=True))

def downgrade():
    op.drop_constraint('ProtoOrder_ibfk_10', 'ProtoOrder', type_='foreignkey')
    op.drop_column('ProtoOrder', 'cart_setting_id')
