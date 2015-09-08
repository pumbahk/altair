"""add_expired_at_to_famiport_order

Revision ID: 348dda4616af
Revises: 1c0db05a4296
Create Date: 2015-08-30 18:07:58.118562

"""

# revision identifiers, used by Alembic.
revision = '348dda4616af'
down_revision = '1c0db05a4296'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('FamiPortOrder', sa.Column('expired_at', sa.DateTime(), nullable=True))

def downgrade():
    op.drop_column('FamiPortOrder', 'expired_at')
