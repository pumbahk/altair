"""add_misc_columns_to_pdmp

Revision ID: 2c844ed2c11
Revises: be240a49b46
Create Date: 2014-08-29 04:10:27.141102

"""

# revision identifiers, used by Alembic.
revision = '2c844ed2c11'
down_revision = 'be240a49b46'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.execute('''
ALTER TABLE PaymentDeliveryMethodPair
    ADD COLUMN payment_start_day_calculation_base INTEGER NOT NULL DEFAULT 1,
    ADD COLUMN payment_start_in_days INTEGER DEFAULT 0,
    ADD COLUMN payment_start_at DATETIME,
    ADD COLUMN payment_due_day_calculation_base INTEGER NOT NULL DEFAULT 1,
    ADD COLUMN payment_due_at DATETIME,
    ADD COLUMN issuing_start_day_calculation_base INTEGER NOT NULL DEFAULT 1,
    ADD COLUMN issuing_end_day_calculation_base INTEGER NOT NULL DEFAULT 1,
    ADD COLUMN issuing_end_in_days INTEGER DEFAULT 364
''')
    op.execute('''
UPDATE PaymentDeliveryMethodPair
SET
    issuing_start_day_calculation_base=IF(issuing_start_at IS NOT NULL, 0, 1),
    issuing_interval_days=IF(issuing_start_at IS NOT NULL, NULL, issuing_interval_days),
    issuing_end_day_calculation_base=IF(issuing_end_at IS NOT NULL, 0, 1),
    issuing_end_in_days=IF(issuing_end_at IS NOT NULL, NULL, issuing_end_in_days)
''')


def downgrade():
    op.execute('''
ALTER TABLE PaymentDeliveryMethodPair
    DROP COLUMN payment_start_day_calculation_base,
    DROP COLUMN payment_start_in_days,
    DROP COLUMN payment_start_at,
    DROP COLUMN payment_due_day_calculation_base,
    DROP COLUMN payment_due_at,
    DROP COLUMN issuing_start_day_calculation_base,
    DROP COLUMN issuing_end_day_calculation_base,
    DROP COLUMN issuing_end_in_days
''')
