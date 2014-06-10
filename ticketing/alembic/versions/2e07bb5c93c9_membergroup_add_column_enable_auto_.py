"""MemberGroup add column enable_auto_input_form

Revision ID: 2e07bb5c93c9
Revises: 536e910477da
Create Date: 2014-06-04 11:48:58.922398

"""

# revision identifiers, used by Alembic.
revision = '2e07bb5c93c9'
down_revision = '536e910477da'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('MemberGroup', sa.Column('enable_auto_input_form', sa.Boolean(), nullable=False,default=True, server_default=text('1')))

def downgrade():
    op.drop_column('MemberGroup', 'enable_auto_input_form')
