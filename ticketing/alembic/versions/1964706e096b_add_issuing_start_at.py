"""add_issuing_start_at_issuing_end_at_payment_due_at_to_order

Revision ID: 1964706e096b
Revises: 3e2e37602d0b
Create Date: 2013-11-29 15:02:40.492401

"""

# revision identifiers, used by Alembic.
revision = '1964706e096b'
down_revision = '3e2e37602d0b'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('Order', sa.Column('issuing_start_at', sa.DateTime(), nullable=True))
    op.add_column('Order', sa.Column('issuing_end_at', sa.DateTime(), nullable=True))
    op.add_column('Order', sa.Column('payment_start_at', sa.DateTime(), nullable=True))
    op.add_column('Order', sa.Column('payment_due_at', sa.DateTime(), nullable=True))
    op.execute('''
    UPDATE `Order` JOIN `SejOrder` ON `Order`.order_no=`SejOrder`.order_no SET `Order`.issuing_start_at=`SejOrder`.ticketing_start_at, `Order`.issuing_end_at=`SejOrder`.ticketing_due_at, `Order`.payment_due_at=`SejOrder`.payment_due_at WHERE `Order`.deleted_at IS NULL;
''')
def downgrade():
    op.drop_column('Order', 'issuing_start_at')
    op.drop_column('Order', 'issuing_end_at')
    op.drop_column('Order', 'payment_start_at')
    op.drop_column('Order', 'payment_due_at')
