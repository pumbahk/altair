"""add card_info to PGWOrderStatus table

Revision ID: 40f9b4556394
Revises: 54ed57d1575b
Create Date: 2020-01-10 09:31:04.544933

"""

# revision identifiers, used by Alembic.
revision = '40f9b4556394'
down_revision = '54ed57d1575b'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('PGWOrderStatus', sa.Column('card_brand_code', sa.Unicode(length=30), nullable=True))
    op.add_column('PGWOrderStatus', sa.Column('card_iin', sa.Unicode(length=6), nullable=True))
    op.add_column('PGWOrderStatus', sa.Column('card_last4digits', sa.Unicode(length=4), nullable=True))
    op.add_column('PGWOrderStatus', sa.Column('ahead_com_cd', sa.Unicode(length=7), nullable=True))
    op.add_column('PGWOrderStatus', sa.Column('approval_no', sa.Unicode(length=7), nullable=True))


def downgrade():
    op.drop_column('PGWOrderStatus', 'card_brand_code')
    op.drop_column('PGWOrderStatus', 'card_iin')
    op.drop_column('PGWOrderStatus', 'card_last4digits')
    op.drop_column('PGWOrderStatus', 'ahead_com_cd')
    op.drop_column('PGWOrderStatus', 'approval_no')

