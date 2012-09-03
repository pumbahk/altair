"""add_row_id_to_seat

Revision ID: 4725c95a84a0
Revises: 408a36838f2e
Create Date: 2012-08-31 17:47:16.845022

"""

# revision identifiers, used by Alembic.
revision = '4725c95a84a0'
down_revision = '408a36838f2e'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('Seat', sa.Column('row_l0_id', sa.String(255)))
    op.create_index('ik_row_l0_id', 'Seat', ['row_l0_id'])

def downgrade():
    op.drop_index('ik_row_l0_id', 'Seat')
    op.drop_column('Seat', 'row_l0_id')
