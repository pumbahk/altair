"""Add columns AugusAccount to toggle new functions

Revision ID: 4bb9691556bf
Revises: 4dee681121d2
Create Date: 2018-08-21 15:37:06.119312

"""

# revision identifiers, used by Alembic.
revision = '4bb9691556bf'
down_revision = '4dee681121d2'

from alembic import op
import sqlalchemy as sa

Identifier = sa.BigInteger


def upgrade():
    op.add_column('AugusAccount',
                  sa.Column('use_numbered_ticket_format', sa.Boolean(), nullable=False, default=False))
    op.add_column('AugusAccount',
                  sa.Column('accept_achievement_request', sa.Boolean(), nullable=False, default=False))
    op.add_column('AugusAccount',
                  sa.Column('accept_putback_request', sa.Boolean(), nullable=False, default=False))
    op.add_column('AugusAccount',
                  sa.Column('enable_auto_distribution_to_own_stock_holder', sa.Boolean(), nullable=False, default=False))
    op.add_column('AugusAccount',
                  sa.Column('enable_unreserved_seat', sa.Boolean(), nullable=False, default=False))


def downgrade():
    op.drop_column('AugusAccount', 'use_numbered_ticket_format')
    op.drop_column('AugusAccount', 'accept_achievement_request')
    op.drop_column('AugusAccount', 'accept_putback_request')
    op.drop_column('AugusAccount', 'enable_auto_distribution_to_own_stock_holder')
    op.drop_column('AugusAccount', 'enable_unreserved_seat')
