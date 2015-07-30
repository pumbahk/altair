"""add_preferences_to_payment_method

Revision ID: 1e5de91b984b
Revises: 585612b4453b
Create Date: 2015-07-22 17:12:53.093450

"""

# revision identifiers, used by Alembic.
revision = '1e5de91b984b'
down_revision = '18cbd130b09d'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    from altair.app.ticketing.payments.plugins import SEJ_DELIVERY_PLUGIN_ID
    op.add_column('PaymentMethod',
        sa.Column('preferences', sa.Unicode(16384), nullable=False, server_default=text(u"'{}'"))
        )
    op.execute("""UPDATE PaymentMethod SET preferences=CONCAT('{"%d":{"hide_voucher":', hide_voucher, '}}')""" % SEJ_DELIVERY_PLUGIN_ID)
    # op.drop_column('PaymentMethod', 'hide_voucher') # DO THIS LATER

def downgrade():
    # op.add_column('PaymentMethod',
    #     sa.Column('hide_voucher', sa.BOOLEAN, nullable=False, server_default=text(u"FALSE"))
    #     )
    hide_voucher_data = []
    bind = op.get_bind()
    for id_, preferences in bind.execute("SELECT id, preferences FROM PaymentMethod"):
        x = json.loads(preferences)
        hide_voucher_data.append((x.get('hide_voucher', False), id_))
    with bind.begin() as ctx:
        for x in hide_voucher_data:
            bind.execute("UPDATE PaymentMethod SET hide_voucher=%s WHERE id=%s", x)
    op.drop_column('PaymentMethod', 'preferences')

