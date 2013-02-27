"""salessegment group also has backend id

Revision ID: 1ce6c0627175
Revises: 26fdc4343dc0
Create Date: 2013-02-27 18:46:20.934779

"""

# revision identifiers, used by Alembic.
revision = '1ce6c0627175'
down_revision = '26fdc4343dc0'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    op.add_column('salessegment_group', sa.Column('backend_id', sa.Integer(), nullable=True))

def downgrade():
    op.drop_column('salessegment_group', 'backend_id')
