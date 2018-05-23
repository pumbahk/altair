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
    op.add_column('ResaleSegment', sa.Column('resale_start_at', sa.DateTime(), nullable=True))
    op.add_column('ResaleSegment', sa.Column('resale_end_at', sa.DateTime(), nullable=True))
    # op.alter_column('ResaleSegment', 'start_at', new_column_name='reception_start_at', existing_type=sa.DateTime(), nullable=True)
    # op.alter_column('ResaleSegment', 'end_at', new_column_name='reception_end_at', existing_type=sa.DateTime(), nullable=True)

def downgrade():
    op.drop_column('ResaleSegment', 'resale_start_at')
    op.drop_column('ResaleSegment', 'resale_end_at')
    # op.alter_column('ResaleSegment', 'reception_start_at', new_column_name='start_at', existing_type=sa.DateTime(), nullable=True)
    # op.alter_column('ResaleSegment', 'reception_end_at', new_column_name='end_at', existing_type=sa.DateTime(), nullable=True)