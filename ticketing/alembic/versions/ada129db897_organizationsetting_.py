"""OrganizationSetting.performance_selector

Revision ID: ada129db897
Revises: 324a22883704
Create Date: 2013-03-21 11:37:33.348812

"""

# revision identifiers, used by Alembic.
revision = 'ada129db897'
down_revision = '324a22883704'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column("OrganizationSetting",
                  sa.Column("performance_selector", sa.Unicode(255)),
                  )
    op.execute("UPDATE OrganizationSetting set performance_selector = 'matchup'")

def downgrade():
    op.drop_column("OrganizationSetting",
                   "performance_selector")
