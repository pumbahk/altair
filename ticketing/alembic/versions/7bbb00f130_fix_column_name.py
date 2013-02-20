"""fix column name

Revision ID: 7bbb00f130
Revises: 498c516acf9d
Create Date: 2013-01-27 19:17:35.452099

"""

# revision identifiers, used by Alembic.
revision = '7bbb00f130'
down_revision = '498c516acf9d'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.execute("ALTER TABLE SalesSegment_PaymentDeliveryMethodPair DROP FOREIGN KEY `SalesSegment_PaymentDeliveryMethodPair_ibfk_1`;")
    op.execute("ALTER TABLE SalesSegment_PaymentDeliveryMethodPair CHANGE COLUMN `payment_delivery_method_pair` `payment_delivery_method_pair_id` bigint(20) DEFAULT NULL;")
    op.execute("ALTER TABLE SalesSegment_PaymentDeliveryMethodPair ADD CONSTRAINT `SalesSegment_PaymentDeliveryMethodPair_ibfk_1` FOREIGN KEY (`payment_delivery_method_pair_id`) REFERENCES `PaymentDeliveryMethodPair` (`id`);")

def downgrade():
    op.execute("ALTER TABLE SalesSegment_PaymentDeliveryMethodPair DROP FOREIGN KEY `SalesSegment_PaymentDeliveryMethodPair_ibfk_1`;")
    op.execute("ALTER TABLE SalesSegment_PaymentDeliveryMethodPair CHANGE COLUMN `payment_delivery_method_pair_id` `payment_delivery_method_pair` bigint(20) DEFAULT NULL;")
    op.execute("ALTER TABLE SalesSegment_PaymentDeliveryMethodPair ADD CONSTRAINT `SalesSegment_PaymentDeliveryMethodPair_ibfk_1` FOREIGN KEY (`payment_delivery_method_pair`) REFERENCES `PaymentDeliveryMethodPair` (`id`);")

