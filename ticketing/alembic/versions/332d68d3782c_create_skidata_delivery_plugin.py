# -*- coding: utf-8 -*-
"""Create Skidata devlivery plugin.

Revision ID: 332d68d3782c
Revises: 3b25f0dfa9a2
Create Date: 2019-10-02 15:26:06.371288

"""

# revision identifiers, used by Alembic.
revision = '332d68d3782c'
down_revision = '3b25f0dfa9a2'

from alembic import op
import sqlalchemy as sa
from altair.app.ticketing.payments.plugins import SKIDATA_QR_DELIVERY_PLUGIN_ID


Identifier = sa.BigInteger


def upgrade():
    op.execute(u"INSERT INTO DeliveryMethodPlugin (id, name) VALUES({0}, 'SKIDATA_QRゲート');"
               .format(SKIDATA_QR_DELIVERY_PLUGIN_ID))


def downgrade():
    op.execute(u"DELETE FROM DeliveryMethodPlugin WHERE id={0};".format(SKIDATA_QR_DELIVERY_PLUGIN_ID))
