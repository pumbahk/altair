"""add start_on,end_on salessegment_group

Revision ID: 220b8dc5b1be
Revises: 3ccdbfde6dfe
Create Date: 2013-02-21 18:49:32.433221

"""

# revision identifiers, used by Alembic.
revision = '220b8dc5b1be'
down_revision = '3ccdbfde6dfe'

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('salessegment_group', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('salessegment_group', sa.Column('end_on', sa.DateTime(), nullable=True))
    op.add_column('salessegment_group', sa.Column('start_on', sa.DateTime(), nullable=True))
    op.add_column('salessegment_group', sa.Column('updated_at', sa.DateTime(), nullable=True))

def downgrade():
    op.drop_column('salessegment_group', 'updated_at')
    op.drop_column('salessegment_group', 'start_on')
    op.drop_column('salessegment_group', 'end_on')
    op.drop_column('salessegment_group', 'created_at')
