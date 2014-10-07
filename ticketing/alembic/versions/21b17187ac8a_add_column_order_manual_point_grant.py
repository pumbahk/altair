"""Add manual_point_grant column to Order

Revision ID: 21b17187ac8a
Revises: 48ef7b667f43
Create Date: 2014-09-12 19:31:01.944806

"""

# revision identifiers, used by Alembic.
revision = '21b17187ac8a'
down_revision = '48ef7b667f43'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column(u'Order', sa.Column(u'manual_point_grant', sa.Boolean, nullable=False, default=False))

def downgrade():
    op.drop_column(u'Order', u'manual_point_grant')
