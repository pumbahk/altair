"""add_event_label_switch

Revision ID: 3a4d337b0d8d
Revises: 36ad59179092
Create Date: 2017-02-03 10:34:26.234443

"""

# revision identifiers, used by Alembic.
revision = '3a4d337b0d8d'
down_revision = '36ad59179092'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('OrganizationSetting', sa.Column('event_label', sa.Boolean(), nullable=False, default=True, server_default=text('1')))

def downgrade():
    op.drop_column('OrganizationSetting', 'event_label')
