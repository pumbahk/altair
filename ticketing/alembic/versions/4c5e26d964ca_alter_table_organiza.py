"""alter table OrganizationSetting add column

Revision ID: 4c5e26d964ca
Revises: 19d54c1f7e06
Create Date: 2013-03-27 13:42:32.996407

"""

# revision identifiers, used by Alembic.
revision = '4c5e26d964ca'
down_revision = '19d54c1f7e06'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column(u'OrganizationSetting', sa.Column('margin_ratio', sa.Numeric(precision=16, scale=2), nullable=False, default=0, server_default='0'))
    op.add_column(u'OrganizationSetting', sa.Column('refund_ratio', sa.Numeric(precision=16, scale=2), nullable=False, default=0, server_default='0'))
    op.add_column(u'OrganizationSetting', sa.Column('printing_fee', sa.Numeric(precision=16, scale=2), nullable=False, default=0, server_default='0'))
    op.add_column(u'OrganizationSetting', sa.Column('registration_fee', sa.Numeric(precision=16, scale=2), nullable=False, default=0, server_default='0'))
    op.drop_column(u'Organization', 'margin_ratio')
    op.drop_column(u'Organization', 'refund_ratio')
    op.drop_column(u'Organization', 'printing_fee')
    op.drop_column(u'Organization', 'registration_fee')

def downgrade():
    op.add_column(u'Organization', sa.Column('margin_ratio', sa.Numeric(precision=16, scale=2), nullable=False))
    op.add_column(u'Organization', sa.Column('refund_ratio', sa.Numeric(precision=16, scale=2), nullable=False))
    op.add_column(u'Organization', sa.Column('printing_fee', sa.Numeric(precision=16, scale=2), nullable=False))
    op.add_column(u'Organization', sa.Column('registration_fee', sa.Numeric(precision=16, scale=2), nullable=False))
    op.drop_column(u'OrganizationSetting', 'margin_ratio')
    op.drop_column(u'OrganizationSetting', 'refund_ratio')
    op.drop_column(u'OrganizationSetting', 'printing_fee')
    op.drop_column(u'OrganizationSetting', 'registration_fee')

