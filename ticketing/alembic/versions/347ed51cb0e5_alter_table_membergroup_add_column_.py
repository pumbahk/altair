"""alter table MemberGroup add column enable_point_input

Revision ID: 347ed51cb0e5
Revises: 2d5d907b18ba
Create Date: 2014-11-14 18:13:14.955676

"""

# revision identifiers, used by Alembic.
revision = '347ed51cb0e5'
down_revision = '2d5d907b18ba'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('MemberGroup', sa.Column('enable_point_input', sa.Boolean(), nullable=False,default=True, server_default=text('1')))

def downgrade():
    op.drop_column('MemberGroup', 'enable_point_input')
