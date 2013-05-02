"""update date unavailable_period_days

Revision ID: 186e089c4c62
Revises: 5ba25a31748
Create Date: 2013-05-02 11:06:34.156358

"""

# revision identifiers, used by Alembic.
revision = '186e089c4c62'
down_revision = '5ba25a31748'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column(u'PaymentDeliveryMethodPair', sa.Column('unavailable_period_days2', sa.Integer, nullable=False, default=0))
    op.execute("""
        UPDATE PaymentDeliveryMethodPair SET unavailable_period_days2 = unavailable_period_days;
    """)
    op.execute("""
        UPDATE PaymentDeliveryMethodPair pdmp, SalesSegment ss, Performance p
        SET pdmp.unavailable_period_days = pdmp.unavailable_period_days2 - (to_days(p.start_on) - to_days(ss.end_at))
        WHERE pdmp.sales_segment_group_id = ss.sales_segment_group_id
        AND ss.performance_id = p.id;
    """)
    op.execute("""
        UPDATE PaymentDeliveryMethodPair SET unavailable_period_days = 0 WHERE unavailable_period_days < 0;
    """)

def downgrade():
    op.execute("""
        UPDATE PaymentDeliveryMethodPair SET unavailable_period_days = unavailable_period_days2;
    """)
    op.drop_column(u'PaymentDeliveryMethodPair', 'unavailable_period_days2')
