"""SalesSegmentGroup.organization_id

Revision ID: 4408494bbb27
Revises: 1661be4d5b4c
Create Date: 2013-08-08 15:57:43.979661

"""

# revision identifiers, used by Alembic.
revision = '4408494bbb27'
down_revision = '1661be4d5b4c'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column("SalesSegmentGroup",
                  sa.Column("organization_id", 
                            Identifier,
                            sa.ForeignKey("Organization.id", name="SalesSegmentGroup_ibfk_3")))


def downgrade():
    op.drop_constraint("SalesSegmentGroup_ibfk_3", "SalesSegmentGroup",
                       type="foreignkey")
    op.drop_column("SalesSegmentGroup", "organization_id")
