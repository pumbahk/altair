"""shipping_address_id is nullable

Revision ID: 3b808f24eb38
Revises: 502ab35cd584
Create Date: 2012-07-27 15:30:42.431544

"""

# revision identifiers, used by Alembic.
revision = '3b808f24eb38'
down_revision = '502ab35cd584'

from alembic import op
import sqlalchemy as sa

Identifier = sa.BigInteger

def upgrade():
    op.alter_column('ticketing_carts', 'shipping_address_id', True, existing_type=Identifier(), existing_nullable=False)

def downgrade():
    op.alter_column('ticketing_carts', 'shipping_address_id', False, existing_type=Identifier(), existing_nullable=True)
