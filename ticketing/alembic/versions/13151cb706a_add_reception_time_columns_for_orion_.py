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

Identifier = sa.BigInteger

def upgrade():
    op.add_column('ResaleSegment', sa.Column('resale_start_at', sa.DateTime(), nullable=True))
    op.add_column('ResaleSegment', sa.Column('resale_end_at', sa.DateTime(), nullable=True))
    sql = "UPDATE ResaleSegment SET resale_start_at = start_at, resale_end_at=end_at;"
    op.execute(sql)

def downgrade():
    op.drop_column('ResaleSegment', 'resale_start_at')
    op.drop_column('ResaleSegment', 'resale_end_at')
