"""add eventticket_pickup,ticket_payment

Revision ID: 2cd70c991fc4
Revises: 4019ba1e72e1
Create Date: 2012-06-23 13:07:17.147813

"""

# revision identifiers, used by Alembic.
revision = '2cd70c991fc4'
down_revision = '4019ba1e72e1'

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('event', sa.Column('ticket_payment', sa.UnicodeText(), nullable=True))
    op.add_column('event', sa.Column('ticket_pickup', sa.UnicodeText(), nullable=True))
    op.drop_column('event', u'place')


def downgrade():
    op.drop_column('event', 'ticket_payment')
    op.drop_column('event', 'ticket_pickup')
    op.add_column('event', sa.Column(u'place', sa.Unicode(length=255), nullable=True))
