"""rename column PaymentDeliveryMethodPair

Revision ID: 4316a6bc8845
Revises: 2d71b810a558
Create Date: 2013-01-24 18:03:21.875519

"""

# revision identifiers, used by Alembic.
revision = '4316a6bc8845'
down_revision = '2d71b810a558'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.execute("""\
ALTER TABLE PaymentDeliveryMethodPair DROP FOREIGN KEY PaymentDeliveryMethodPair_ibfk_1;
ALTER TABLE PaymentDeliveryMethodPair CHANGE COLUMN sales_segment_id sales_segment_group_id BIGINT;
ALTER TABLE PaymentDeliveryMethodPair ADD CONSTRAINT PaymentDeliveryMethodPair_ibfk_1 FOREIGN KEY (sales_segment_group_id) REFERENCES SalesSegmentGroup (id);
""")


def downgrade():
    op.execute("""\
ALTER TABLE PaymentDeliveryMethodPair DROP FOREIGN KEY PaymentDeliveryMethodPair_ibfk_1;
ALTER TABLE PaymentDeliveryMethodPair CHANGE COLUMN sales_segment_group_id sales_segment_id BIGINT;
ALTER TABLE PaymentDeliveryMethodPair ADD CONSTRAINT PaymentDeliveryMethodPair_ibfk_1 FOREIGN KEY (sales_segment_id) REFERENCES SalesSegmentGroup (id);
""")
