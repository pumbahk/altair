"""add_attributes_to_delivery_method

Revision ID: 585612b4453b
Revises: 38e00b9843c3
Create Date: 2015-07-08 12:07:05.010358

"""

# revision identifiers, used by Alembic.
revision = '585612b4453b'
down_revision = '38e00b9843c3'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf
from altair.models import JSONEncodedDict
import json

Identifier = sa.BigInteger


def upgrade():
    from altair.app.ticketing.payments.plugins import SEJ_DELIVERY_PLUGIN_ID
    op.add_column('DeliveryMethod',
        sa.Column('preferences', sa.Unicode(16384), nullable=False, server_default=text(u"'{}'"))
        )
    op.execute("""UPDATE DeliveryMethod SET preferences=CONCAT('{"%d":{"hide_voucher":', hide_voucher, '}}')""" % SEJ_DELIVERY_PLUGIN_ID)
    # op.drop_column('DeliveryMethod', 'hide_voucher') # DO THIS LATER

def downgrade():
    # op.add_column('DeliveryMethod',
    #     sa.Column('hide_voucher', sa.BOOLEAN, nullable=False, server_default=text(u"FALSE"))
    #     )
    hide_voucher_data = []
    bind = op.get_bind()
    for id_, preferences in bind.execute("SELECT id, preferences FROM DeliveryMethod"):
        x = json.loads(preferences)
        hide_voucher_data.append((x.get('hide_voucher', False), id_))
    with bind.begin() as ctx:
        for x in hide_voucher_data:
            bind.execute("UPDATE DeliveryMethod SET hide_voucher=%s WHERE id=%s", x)
    op.drop_column('DeliveryMethod', 'preferences')
