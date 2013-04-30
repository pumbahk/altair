"""LotEntryWish.order

Revision ID: d0baadd71cc
Revises: 497bd17d9955
Create Date: 2013-04-26 18:48:36.776828

"""

# revision identifiers, used by Alembic.
revision = 'd0baadd71cc'
down_revision = '497bd17d9955'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('LotEntryWish',
                  sa.Column("order_id", Identifier, sa.ForeignKey('Order.id', name='LotEntryWish_ibfk_3')))


def downgrade():
    op.drop_constraint('LotEntryWish_ibfk_3', 'LotEntryWish', type='foreignkey')
    op.drop_column('LotEntryWish', 'order_id')
