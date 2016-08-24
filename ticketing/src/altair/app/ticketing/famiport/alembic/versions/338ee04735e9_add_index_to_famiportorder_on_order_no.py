"""add index to FamiPortOrder on order_no

Revision ID: 338ee04735e9
Revises: d068c02f6e6
Create Date: 2016-08-04 15:43:22.919836

"""

# revision identifiers, used by Alembic.
revision = '338ee04735e9'
down_revision = 'd068c02f6e6'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_index('ix_famiport_order_no', 'FamiPortOrder', ['order_no'])

def downgrade():
    op.drop_index('ix_famiport_order_no', 'FamiPortOrder')
