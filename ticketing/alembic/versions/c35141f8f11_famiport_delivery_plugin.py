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
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    from altair.app.ticketing.payments.plugins import FAMIPORT_DELIVERY_PLUGIN_ID
    sql = u"INSERT INTO DeliveryMethodPlugin (id, name) VALUES({plugin_id}, 'ファミポート引取') ON DUPLICATE KEY UPDATE id={plugin_id} ;".format(plugin_id=FAMIPORT_DELIVERY_PLUGIN_ID)  # noqa
    op.execute(sql)


def downgrade():
    from altair.app.ticketing.payments.plugins import FAMIPORT_DELIVERY_PLUGIN_ID
    sql = 'DELETE FROM DeliveryMethodPlugin WHERE id={plugin_id} AND (SELECT COUNT(*) FROM DeliveryMethod WHERE DeliveryMethod.delivery_plugin_id={plugin_id}) = 0;'.format(plugin_id=FAMIPORT_DELIVERY_PLUGIN_ID)  # noqa
    op.execute(sql)
