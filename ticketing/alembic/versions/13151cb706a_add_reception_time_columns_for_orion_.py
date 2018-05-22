"""add reception time columns for orion performance

Revision ID: 13151cb706a
Revises: 3cd361e34c44
Create Date: 2018-05-22 13:47:57.941135

"""

# revision identifiers, used by Alembic.
revision = '13151cb706a'
down_revision = '3cd361e34c44'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger

def upgrade():
    op.add_column('OrionPerformance', sa.Column('resale_start_at', sa.DateTime(), nullable=True))
    op.add_column('OrionPerformance', sa.Column('resale_end_at', sa.DateTime(), nullable=True))

def downgrade():
    op.drop_column('OrionPerformance', 'resale_start_at')
    op.drop_column('OrionPerformance', 'resale_end_at')
