"""hide voucher

Revision ID: 3c09f04450b3
Revises: 53a1eba253dd
Create Date: 2013-05-31 17:07:15.608555

"""

# revision identifiers, used by Alembic.
revision = '3c09f04450b3'
down_revision = '53a1eba253dd'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column("PaymentMethod",
                  sa.Column("hide_voucher", sa.Boolean, server_default=text('0')))
    op.add_column("DeliveryMethod",
                  sa.Column("hide_voucher", sa.Boolean, server_default=text('0')))

def downgrade():
    op.drop_column("PaymentMethod", "hide_voucher")
    op.drop_column("DeliveryMethod", "hide_voucher")
