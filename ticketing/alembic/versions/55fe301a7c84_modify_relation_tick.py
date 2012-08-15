"""modify_relation_ticketbundle_productitem

Revision ID: 55fe301a7c84
Revises: 3584d649de05
Create Date: 2012-08-15 13:22:13.548996

"""

# revision identifiers, used by Alembic.
revision = '55fe301a7c84'
down_revision = '3584d649de05'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
Identifier = sa.BigInteger

def upgrade():
    op.create_table('TicketBundle_ProductItem',
                    sa.Column('ticket_bundle_id', Identifier(), nullable=False),
                    sa.Column('product_item_id', Identifier(), nullable=False),
                    sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
                    sa.ForeignKeyConstraint(['product_item_id'], ['ProductItem.id'], ),
                    sa.ForeignKeyConstraint(['ticket_bundle_id'], ['TicketBundle.id'], ),
                    sa.PrimaryKeyConstraint('ticket_bundle_id', 'product_item_id')
                    )

def downgrade():
    op.drop_table('TicketBundle_ProductItem')
