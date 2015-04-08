"""famiport_payment_plugin

Revision ID: 4855569c078d
Revises: 18b5da6a9ed5
Create Date: 2015-04-09 00:37:48.715650

"""

# revision identifiers, used by Alembic.
revision = '4855569c078d'
down_revision = '18b5da6a9ed5'

from alembic import op
import sqlalchemy as sa
Identifier = sa.BigInteger


def upgrade():
    from altair.app.ticketing.payments.plugins import FAMIPORT_PAYMENT_PLUGIN_ID
    op.execute(u"""INSERT INTO PaymentMethodPlugin (id, name) VALUES (%d, 'ファミポート決済');""" % FAMIPORT_PAYMENT_PLUGIN_ID)


def downgrade():
    from altair.app.ticketing.payments.plugins import FAMIPORT_PAYMENT_PLUGIN_ID
    op.execute(u"""DELETE FROM PaymentMethodPlugin WHERE id=%d;""" % FAMIPORT_PAYMENT_PLUGIN_ID)
