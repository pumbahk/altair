"""data migration SalesSegmentGroup.organization_id

Revision ID: 48bef89dedee
Revises: 4408494bbb27
Create Date: 2013-08-08 16:01:56.833111

"""

# revision identifiers, used by Alembic.
revision = '48bef89dedee'
down_revision = '4408494bbb27'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    sql = """\
    UPDATE SalesSegmentGroup
    JOIN Event
    ON Event.id = SalesSegmentGroup.event_id
    SET SalesSegmentGroup.organization_id = Event.organization_id
"""
    op.execute(sql)

def downgrade():
    sql = """\
    UPDATE SalesSegmentGroup
    SET SalesSegmentGroup.organization_id = NULL
"""
    op.execute(sql)

