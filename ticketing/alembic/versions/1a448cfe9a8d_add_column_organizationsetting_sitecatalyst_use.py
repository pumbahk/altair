"""empty message

Revision ID: 1a448cfe9a8d
Revises: 5a3713bf896a
Create Date: 2015-01-30 12:10:07.314153

"""

# revision identifiers, used by Alembic.
revision = '1a448cfe9a8d'
down_revision = '5a3713bf896a'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('OrganizationSetting', sa.Column('sitecatalyst_use', sa.Boolean(), nullable=True, default=False))
    op.execute("UPDATE OrganizationSetting SET sitecatalyst_use = true WHERE organization_id = 15")

def downgrade():
    op.drop_column('OrganizationSetting', 'sitecatalyst_use')
