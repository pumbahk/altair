"""alter table Membership, MemberGroup move enable_auto_input_form

Revision ID: 30afb058c47
Revises: 3241f7f547dc
Create Date: 2014-12-25 16:37:14.423416

"""

# revision identifiers, used by Alembic.
revision = '30afb058c47'
down_revision = '3241f7f547dc'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.drop_column('MemberGroup', 'enable_auto_input_form')
    op.add_column('Membership', sa.Column('enable_auto_input_form', sa.Boolean(), nullable=False,default=True, server_default=text('1')))
    op.execute(u"UPDATE Membership SET enable_auto_input_form = 0 WHERE id in (6, 17, 20, 25, 48)")
    op.drop_column('MemberGroup', 'enable_point_input')
    op.add_column('Membership', sa.Column('enable_point_input', sa.Boolean(), nullable=False,default=True, server_default=text('1')))

def downgrade():
    op.drop_column('Membership', 'enable_auto_input_form')
    op.add_column('MemberGroup', sa.Column('enable_auto_input_form', sa.Boolean(), nullable=False,default=True, server_default=text('1')))
    op.execute(u"UPDATE MemberGroup SET enable_auto_input_form = 0 WHERE id in (300107, 300122, 300013, 300121, 300103, 300146)")
    op.drop_column('Membership', 'enable_point_input')
    op.add_column('MemberGroup', sa.Column('enable_point_input', sa.Boolean(), nullable=False,default=True, server_default=text('1')))
