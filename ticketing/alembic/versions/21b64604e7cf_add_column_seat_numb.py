"""add column seat_number to Seat

Revision ID: 21b64604e7cf
Revises: 40e909e8bf3c
Create Date: 2012-08-17 14:36:12.784527

"""

# revision identifiers, used by Alembic.
revision = '21b64604e7cf'
down_revision = '40e909e8bf3c'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('Seat', sa.Column('seat_no', sa.String(255)))

def downgrade():
    op.drop_column('Seat', 'seat_no')

