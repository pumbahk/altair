"""alter table OrganizationSetting add column enable_smartphone_cart

Revision ID: 536e910477da
Revises: 379d8f5fb25
Create Date: 2014-06-03 14:59:32.740626

"""

# revision identifiers, used by Alembic.
revision = '536e910477da'
down_revision = '141b0368d69f'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('OrganizationSetting', sa.Column('enable_smartphone_cart', sa.Boolean(), nullable=False, default=False, server_default=text('0')))
    sql = """\
    UPDATE OrganizationSetting
    SET enable_smartphone_cart = 1
    WHERE organization_id in (4, 15, 24, 25, 26, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37);
    """
    op.execute(sql)
def downgrade():
    op.drop_column('OrganizationSetting', 'enable_smartphone_cart')
