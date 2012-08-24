"""add payment and delivery method description.

Revision ID: 10ed91837586
Revises: 406252f94050
Create Date: 2012-08-23 17:38:17.085450

"""

# revision identifiers, used by Alembic.
revision = '10ed91837586'
down_revision = '406252f94050'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('PaymentMethod', sa.Column('description', sa.String(2000)))
    op.add_column('DeliveryMethod', sa.Column('description', sa.String(2000)))

def downgrade():
    op.drop_column('PaymentMethod', 'description') 
    op.drop_column('DeliveryMethod', 'description') 
