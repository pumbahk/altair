"""improve_orders_refund_export_result

Revision ID: 133d6f048788
Revises: 76aefb1573c
Create Date: 2018-06-21 10:46:20.963241

"""

# revision identifiers, used by Alembic.
revision = '133d6f048788'
down_revision = '76aefb1573c'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_index('barcode_number', 'SejTicket', ['barcode_number'])
    op.create_index('ticket_barcode_number', 'SejRefundTicket', ['ticket_barcode_number'])


def downgrade():
    op.drop_index('barcode_number', 'SejTicket')
    op.drop_index('ticket_barcode_number', 'SejRefundTicket')
