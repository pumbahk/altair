"""add field performance 

Revision ID: 52602e18e0ff
Revises: 1ba3266beb3
Create Date: 2012-05-25 20:03:34.298497

"""

# revision identifiers, used by Alembic.
revision = '52602e18e0ff'
down_revision = '1ba3266beb3'

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column("performance", sa.Column("purchase_link", sa.UnicodeText))

def downgrade():
    op.drop_column("performance", "purchase_link")
