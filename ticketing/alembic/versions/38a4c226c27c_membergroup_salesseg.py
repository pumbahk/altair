"""MemberGroup_SalesSegmentGroup

Revision ID: 38a4c226c27c
Revises: 48bef89dedee
Create Date: 2013-08-09 10:55:11.909559

"""

# revision identifiers, used by Alembic.
revision = '38a4c226c27c'
down_revision = '48bef89dedee'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table('MemberGroup_SalesSegmentGroup',
                    sa.Column('id', Identifier, primary_key=True),
                    sa.Column('membergroup_id', Identifier,
                              sa.ForeignKey('MemberGroup.id', name="MemberGroup_SalesSegmentGroup_ibfk1")),
                    sa.Column('sales_segment_group_id', Identifier,
                              sa.ForeignKey('SalesSegmentGroup.id', name="MemberGroup_SalesSegmentGroup_ibfk2")),
                    sa.UniqueConstraint('membergroup_id', 'sales_segment_group_id'),
                )

def downgrade():
    op.drop_table('MemberGroup_SalesSegmentGroup')
