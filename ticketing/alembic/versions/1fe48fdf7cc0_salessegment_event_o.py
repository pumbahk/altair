"""SalesSegment event organization

Revision ID: 1fe48fdf7cc0
Revises: 399b88245d9
Create Date: 2013-08-08 15:03:59.179277

"""

# revision identifiers, used by Alembic.
revision = '1fe48fdf7cc0'
down_revision = '399b88245d9'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column("SalesSegment",
                  sa.Column("event_id", Identifier,
                            sa.ForeignKey("Event.id",
                                          name="SalesSegment_ibfk_4")))
    op.add_column("SalesSegment",
                  sa.Column("organization_id", Identifier,
                            sa.ForeignKey("Organization.id",
                                          name="SalesSegment_ibfk_5")))

def downgrade():
    op.drop_constraint("SalesSegment_ibfk_5",
                       "SalesSegment",type="foreignkey")
    op.drop_column("SalesSegment", "organization_id")
    op.drop_constraint("SalesSegment_ibfk_4", 
                       "SalesSegment", type="foreignkey")
    op.drop_column("SalesSegment", "event_id")
