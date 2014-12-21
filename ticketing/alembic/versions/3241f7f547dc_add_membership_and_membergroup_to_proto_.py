"""add_membership_and_membergroup_to_proto_order

Revision ID: 3241f7f547dc
Revises: 83224a82fa6
Create Date: 2014-12-21 13:18:07.794650

"""

# revision identifiers, used by Alembic.
revision = '3241f7f547dc'
down_revision = '83224a82fa6'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('ProtoOrder', sa.Column('membership_id', Identifier(), sa.ForeignKey('Membership.id', name='ProtoOrder_ibfk_12'), nullable=True))
    op.add_column('ProtoOrder', sa.Column('membergroup_id', Identifier(), sa.ForeignKey('MemberGroup.id', name='ProtoOrer_ibfk_13'), nullable=True))

def downgrade():
    op.drop_constraint('ProtoOrder_ibfk_12', 'ProtoOrder', type_='foreignkey')
    op.drop_constraint('ProtoOrder_ibfk_13', 'ProtoOrder', type_='foreignkey')
    op.drop_column('ProtoOrder', 'membergroup_id')
    op.drop_column('ProtoOrder', 'membership_id')
