"""Add column OrganizationSetting for PaymentGW.

Revision ID: 3cd6601615a3
Revises: 3a31f6169bd1
Create Date: 2019-04-25 15:34:48.282642

"""

# revision identifiers, used by Alembic.
revision = '3cd6601615a3'
down_revision = '3a31f6169bd1'

from alembic import op
import sqlalchemy as sa

Identifier = sa.BigInteger


def upgrade():
    op.add_column('OrganizationSetting', sa.Column('pgw_sub_service_id', sa.Unicode(50), nullable=True))


def downgrade():
    op.drop_column('OrganizationSetting', 'pgw_sub_service_id')
