# -*- coding: utf-8 -*-
"""famiport_delivery_plugin

Revision ID: c35141f8f11
Revises: 4855569c078d
Create Date: 2015-04-09 02:17:16.986653

"""

# revision identifiers, used by Alembic.
revision = 'c35141f8f11'
down_revision = '4855569c078d'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    from altair.app.ticketing.payments.plugins import FAMIPORT_DELIVERY_PLUGIN_ID
    op.execute(u"INSERT INTO DeliveryMethodPlugin (id, name) VALUES(%d, 'ファミポート引取');" % FAMIPORT_DELIVERY_PLUGIN_ID)


def downgrade():
    from altair.app.ticketing.payments.plugins import FAMIPORT_DELIVERY_PLUGIN_ID
    op.execute(u"DELETE FROM DeliveryMethodPlugin WHERE id=%d;" % FAMIPORT_DELIVERY_PLUGIN_ID)
