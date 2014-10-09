"""add_nwts_params_to_sej_tenant

Revision ID: 2d5d907b18ba
Revises: 2546dac97173
Create Date: 2014-10-01 18:58:29.164245

"""

# revision identifiers, used by Alembic.
revision = '2d5d907b18ba'
down_revision = '2546dac97173'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('SejTenant', sa.Column('nwts_endpoint_url', sa.Unicode(255), nullable=True))
    op.add_column('SejTenant', sa.Column('nwts_terminal_id', sa.Unicode(255), nullable=True))
    op.add_column('SejTenant', sa.Column('nwts_password', sa.Unicode(255), nullable=True))
    op.add_column('SejRefundEvent', sa.Column('nwts_endpoint_url', sa.Unicode(255), nullable=True))
    op.add_column('SejRefundEvent', sa.Column('nwts_terminal_id', sa.Unicode(255), nullable=True))
    op.add_column('SejRefundEvent', sa.Column('nwts_password', sa.Unicode(255), nullable=True))

def downgrade():
    op.drop_column('SejTenant', 'nwts_endpoint_url')
    op.drop_column('SejTenant', 'nwts_terminal_id')
    op.drop_column('SejTenant', 'nwts_password')
    op.drop_column('SejRefundEvent', 'nwts_endpoint_url')
    op.drop_column('SejRefundEvent', 'nwts_terminal_id')
    op.drop_column('SejRefundEvent', 'nwts_password')
