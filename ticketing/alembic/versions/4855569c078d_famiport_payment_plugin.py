# -*- coding: utf-8 -*-
"""famiport_payment_plugin

Revision ID: 4855569c078d
Revises: 10ffc65de6c5
Create Date: 2015-04-09 00:37:48.715650

"""

# revision identifiers, used by Alembic.
revision = '4855569c078d'
down_revision = '10ffc65de6c5'

from alembic import op
import sqlalchemy as sa
Identifier = sa.BigInteger


def upgrade():
    from altair.app.ticketing.payments.plugins import FAMIPORT_PAYMENT_PLUGIN_ID
    sql = u"""INSERT INTO PaymentMethodPlugin (id, name) VALUES ({plugin_id}, 'ファミポート決済') ON DUPLICATE KEY UPDATE id={plugin_id};""".format(plugin_id=FAMIPORT_PAYMENT_PLUGIN_ID)  # noqa
    op.execute(sql)


def downgrade():
    from altair.app.ticketing.payments.plugins import FAMIPORT_PAYMENT_PLUGIN_ID
    sql = u'DELETE FROM PaymentMethodPlugin WHERE id={plugin_id} AND (SELECT COUNT(*) FROM PaymentMethod WHERE PaymentMethod.payment_plugin_id={plugin_id}) = 0;'.format(plugin_id=FAMIPORT_PAYMENT_PLUGIN_ID)  # noqa
    op.execute(sql)
