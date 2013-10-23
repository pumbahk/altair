# -*- coding: utf-8 -*-

"""delete bank transfer

Revision ID: 246e00308204
Revises: 10e7c48c9b2e
Create Date: 2013-10-22 11:49:39.199333

"""

# revision identifiers, used by Alembic.
revision = '246e00308204'
down_revision = '10e7c48c9b2e'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.execute(u"DELETE FROM PaymentMethodPlugin WHERE id = 5")

def downgrade():
    op.execute(u"INSERT INTO PaymentMethodPlugin (id, name) VALUES (5, '銀行振込')")

