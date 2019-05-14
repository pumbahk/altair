"""add column enable_password

Revision ID: 14814b6b5f89
Revises: bf3e4743bea
Create Date: 2019-03-13 16:55:24.681808

"""

# revision identifiers, used by Alembic.
revision = '14814b6b5f89'
down_revision = 'bf3e4743bea'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('OrganizationSetting',
                  sa.Column('enable_review_password', sa.Boolean(), nullable=False, default=False, server_default=text('0')))
    op.add_column('EventSetting',
                  sa.Column('event_enable_review_password', sa.Boolean(), nullable=False, default=False, server_default=text('0')))

def downgrade():
    op.drop_column('OrganizationSetting', 'enable_review_password')
    op.drop_column('EventSetting', 'event_enable_review_password')
