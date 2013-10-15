"""add_sej_order_id_to_SejTicket

Revision ID: 587cd54b6dfc
Revises: 1c5a9494dd9a
Create Date: 2013-10-11 13:13:36.647051

"""

# revision identifiers, used by Alembic.
revision = '587cd54b6dfc'
down_revision = '1c5a9494dd9a'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('SejTicket', sa.Column('sej_order_id', Identifier(), nullable=False))
    op.execute('UPDATE SejTicket JOIN SejOrder ON SejTicket.order_no=SejOrder.order_no SET SejTicket.sej_order_id=SejOrder.id WHERE SejOrder.branch_no=1;')
    op.execute('''
INSERT INTO SejTicket
(
    sej_order_id,
    order_no,
    ticket_type,
    barcode_number,
    event_name,
    performance_name,
    performance_datetime,
    ticket_template_id,
    ticket_data_xml,
    ticket_idx,
    product_item_id,
    created_at,
    updated_at,
    deleted_at
)
SELECT
    SejOrder.id,
    SejOrder.order_no,
    SejTicket_parent.ticket_type,
    SejTicket_parent.barcode_number,
    SejTicket_parent.event_name,
    SejTicket_parent.performance_name,
    SejTicket_parent.performance_datetime,
    SejTicket_parent.ticket_template_id,
    SejTicket_parent.ticket_data_xml,
    SejTicket_parent.ticket_idx,
    SejTicket_parent.product_item_id,
    SejOrder.created_at,
    SejOrder.updated_at,
    SejOrder.deleted_at
FROM 
    SejOrder
    JOIN SejTicket SejTicket_parent ON SejOrder.order_no=SejTicket_parent.order_no
WHERE
    SejOrder.branch_no <> 1
''')
    op.create_foreign_key('SejTicket_ibfk_3', 'SejTicket', 'SejOrder', ['sej_order_id'], ['id'], ondelete='CASCADE')

def downgrade():
    op.drop_constraint('SejTicket_ibfk_3', 'SejTicket', type='foreignkey')
    op.execute('DELETE SejTicket FROM SejTicket JOIN SejOrder ON SejTicket.sej_order_id=SejOrder.id WHERE SejOrder.branch_no <> 1')
    op.drop_column('SejTicket', 'sej_order_id')
