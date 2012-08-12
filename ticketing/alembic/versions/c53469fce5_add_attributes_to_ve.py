"""add_attributes_to_Venue

Revision ID: c53469fce5
Revises: 4b3401617faa
Create Date: 2012-08-13 05:41:40.408970

"""

# revision identifiers, used by Alembic.
revision = 'c53469fce5'
down_revision = '4b3401617faa'

from alembic import op
import sqlalchemy as sa

Identifier = sa.BigInteger

def upgrade():
    op.add_column('Venue', sa.Column('attributes', sa.String(16384)))

def downgrade():
    op.drop_column('Venue', 'attributes')
