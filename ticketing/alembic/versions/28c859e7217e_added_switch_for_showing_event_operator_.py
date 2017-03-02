"""added_switch_for_showing_event_operator_and_sales_person

Revision ID: 28c859e7217e
Revises: 5936c72c6490
Create Date: 2017-02-24 16:41:49.676866

"""

# revision identifiers, used by Alembic.
revision = '28c859e7217e'
down_revision = '5936c72c6490'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('OrganizationSetting', sa.Column('show_event_op_and_sales', sa.Boolean(), nullable=False, default=False, server_default=text('0')))

def downgrade():
    op.drop_column('OrganizationSetting', 'show_event_op_and_sales')
