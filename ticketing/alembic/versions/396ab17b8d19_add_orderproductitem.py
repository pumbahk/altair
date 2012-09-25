"""add OrderProductItem.issued_at

Revision ID: 396ab17b8d19
Revises: 423bbf5b2949
Create Date: 2012-09-25 10:20:36.933071

"""

# revision identifiers, used by Alembic.
revision = '396ab17b8d19'
down_revision = '423bbf5b2949'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger

def upgrade():
    op.add_column(u'OrderedProductItemToken', sa.Column('issued_at', sa.DateTime(), nullable=True))
    op.add_column(u'OrderedProductItem', sa.Column('issued_at', sa.DateTime(), nullable=True))
    op.add_column(u'Order', sa.Column('issued_at', sa.DateTime(), nullable=True))

    op.add_column(u'OrderedProductItemToken', sa.Column('printed_at', sa.DateTime(), nullable=True))
    op.add_column(u'OrderedProductItem', sa.Column('printed_at', sa.DateTime(), nullable=True))
    op.add_column(u'Order', sa.Column('printed_at', sa.DateTime(), nullable=True))

def downgrade():
    op.drop_column(u'OrderedProductItemToken', 'issued_at')
    op.drop_column(u'OrderedProductItem', 'issued_at')
    op.drop_column(u'Order', 'issued_at')
    op.drop_column(u'OrderedProductItemToken', 'printed_at')
    op.drop_column(u'OrderedProductItem', 'printed_at')
    op.drop_column(u'Order', 'printed_at')
