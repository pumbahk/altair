"""add owner phone number to OrionTicketPhone

Revision ID: 41e3c7e113c0
Revises: 267bd8f6b530
Create Date: 2018-03-14 13:34:08.514260

"""

# revision identifiers, used by Alembic.
revision = '41e3c7e113c0'
down_revision = '267bd8f6b530'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger

def upgrade():
    op.add_column('OrionTicketPhone', sa.Column('owner_phone_number', sa.String(length=255), nullable=False, default=''))
    op.add_column('OrionTicketPhone', sa.Column('sent_at', sa.TIMESTAMP(), nullable=True))
    op.add_column('OrionTicketPhone', sa.Column('sent', sa.Boolean(), default=False, server_default='0'))
    op.create_index('idx_OrionTicketPhone_owner_phone_number', 'OrionTicketPhone', ['owner_phone_number'])
    op.create_index('idx_OrionTicketPhone_sent', 'OrionTicketPhone', ['sent'])

    conn = op.get_bind()
    # add phone number to owner_phone_number from shipping address
    with conn.begin():
        conn.execute("update OrionTicketPhone otp join `Order` o on o.order_no = otp.order_no join ShippingAddress sa on sa.id = o.shipping_address_id set otp.owner_phone_number = sa.tel_1 where otp.order_no != '';")
        conn.execute("update OrionTicketPhone otp join LotEntry e on e.entry_no = otp.entry_no join ShippingAddress sa on sa.id = e.shipping_address_id set otp.owner_phone_number = sa.tel_1 where otp.order_no = '' and otp.entry_no != '';")


def downgrade():
    op.drop_index('idx_OrionTicketPhone_owner_phone_number', 'OrionTicketPhone')
    op.drop_index('idx_OrionTicketPhone_sent', 'OrionTicketPhone')
    op.drop_column('OrionTicketPhone', 'owner_phone_number')
    op.drop_column('OrionTicketPhone', 'sent_at')
    op.drop_column('OrionTicketPhone', 'sent')
