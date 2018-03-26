"""add phone_verify_enabled to OrionPerformance

Revision ID: 3835e1ca503b
Revises: daa86477ebb
Create Date: 2018-03-26 10:40:05.737831

"""

# revision identifiers, used by Alembic.
revision = '3835e1ca503b'
down_revision = 'daa86477ebb'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('OrionPerformance', sa.Column('phone_verify_disabled', sa.Boolean(), nullable=True))

def downgrade():
    op.drop_column('OrionPerformance', 'phone_verify_disabled')
