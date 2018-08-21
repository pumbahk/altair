"""Add column AugusSeat ticket_number for Seiriken

Revision ID: 1d6f11b5d485
Revises: 4bb9691556bf
Create Date: 2018-08-21 15:45:02.342776

"""

# revision identifiers, used by Alembic.
revision = '1d6f11b5d485'
down_revision = '4bb9691556bf'

from alembic import op
import sqlalchemy as sa

Identifier = sa.BigInteger


def upgrade():
    op.add_column('AugusSeat',
                  sa.Column('ticket_number', sa.Integer(), nullable=True))


def downgrade():
    op.drop_column('AugusSeat', 'ticket_number')
