"""add_system_fee_template

Revision ID: 18849a570d67
Revises: 378db2b9f0bd
Create Date: 2013-09-06 20:15:59.808715

"""

# revision identifiers, used by Alembic.
revision = '18849a570d67'
down_revision = '378db2b9f0bd'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger

def upgrade():
    op.add_column('OrganizationSetting', sa.Column('system_fee', sa.Numeric(precision=16, scale=2), nullable=False, default=0))
    op.add_column('OrganizationSetting', sa.Column('system_fee_type', sa.Integer(), nullable=False, default=0)) # once
    
def downgrade():
    op.drop_column('OrganizationSetting', 'system_fee')
    op.drop_column('OrganizationSetting', 'system_fee_type')
