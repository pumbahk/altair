# encoding: utf-8
"""add_free_payment_plugin

Revision ID: 1261b43ea7c7
Revises: 56a8429afd99
Create Date: 2015-02-28 12:55:28.312842

"""

# revision identifiers, used by Alembic.
revision = '1261b43ea7c7'
down_revision = '56a8429afd99'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    from altair.app.ticketing.payments.plugins import FREE_PAYMENT_PLUGIN_ID
    op.execute(u"""INSERT INTO PaymentMethodPlugin (id, name) VALUES (%d, '無料');""" % FREE_PAYMENT_PLUGIN_ID)

def downgrade():
    from altair.app.ticketing.payments.plugins import FREE_PAYMENT_PLUGIN_ID
    op.execute(u"""DELETE FROM PaymentMethodPlugin WHERE id=%d;""" % FREE_PAYMENT_PLUGIN_ID)
