# -*- coding: utf-8 -*-
"""add web_coupon_delivery_plugin

Revision ID: 312aad5f5c92
Revises: 1569761b748d
Create Date: 2019-09-05 10:06:08.113863

"""

# revision identifiers, used by Alembic.
revision = '312aad5f5c92'
down_revision = '1569761b748d'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger

from altair.app.ticketing.payments.plugins import WEB_COUPON_DELIVERY_PLUGIN_ID


def upgrade():
    op.execute(u"INSERT INTO DeliveryMethodPlugin (id, name) VALUES({0}, 'WEBクーポン引取');"
               .format(WEB_COUPON_DELIVERY_PLUGIN_ID))


def downgrade():
    op.execute(u"DELETE FROM DeliveryMethodPlugin WHERE id={0};".format(WEB_COUPON_DELIVERY_PLUGIN_ID))
