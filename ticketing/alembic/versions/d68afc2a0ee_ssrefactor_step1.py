"""ssrefactor_step1

Revision ID: d68afc2a0ee
Revises: 136af24cc0c
Create Date: 2013-01-06 21:28:22.588864

"""

# revision identifiers, used by Alembic.
revision = 'd68afc2a0ee'
#down_revision = '136af24cc0c'
down_revision = '4617bbfc3587'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    # https://dev.ticketstar.jp/lodgeit/show/403/
    op.execute("""
CREATE TABLE `SalesSegmentGroup` (
    `id` bigint(20) NOT NULL AUTO_INCREMENT,
    `name` varchar(255) DEFAULT NULL,
    `kind` varchar(255) DEFAULT NULL,
    `start_at` datetime DEFAULT NULL,
    `end_at` datetime DEFAULT NULL,
    `upper_limit` int(11) DEFAULT NULL,
    `seat_choice` tinyint(1) DEFAULT NULL,
    `event_id` bigint(20) DEFAULT NULL,
    `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
    `deleted_at` timestamp NULL DEFAULT NULL,
    `public` tinyint(1) NOT NULL DEFAULT '1',
    PRIMARY KEY (`id`),
    KEY `event_id` (`event_id`),
    KEY `ix_SalesSegmentGroup_deleted_at` (`deleted_at`),
    CONSTRAINT `SalesSegmentGroup_ibfk_1` FOREIGN KEY (`event_id`) REFERENCES `Event` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
    """)
    op.execute("""
LOCK TABLES SalesSegment READ, SalesSegmentGroup WRITE, MemberGroup_SalesSegment WRITE, Product WRITE, PaymentDeliveryMethodPair WRITE, Lot WRITE, ticketing_carts WRITE;
    """)
    op.execute("""
INSERT INTO SalesSegmentGroup SELECT * FROM SalesSegment;
    """)
    op.execute("""
ALTER TABLE MemberGroup_SalesSegment DROP FOREIGN KEY MemberGroup_SalesSegment_ibfk_2;
    """)
    op.execute("""
ALTER TABLE Product DROP FOREIGN KEY Product_ibfk_1;
    """)
    op.execute("""
ALTER TABLE PaymentDeliveryMethodPair DROP FOREIGN KEY PaymentDeliveryMethodPair_ibfk_1;
    """)
    op.execute("""
ALTER TABLE ticketing_carts DROP FOREIGN KEY ticketing_carts_ibfk_5;
    """)
    op.execute("""
ALTER TABLE Lot DROP FOREIGN KEY Lot_ibfk_2;
    """)
    op.execute("""
ALTER TABLE MemberGroup_SalesSegment ADD CONSTRAINT MemberGroup_SalesSegment_ibfk_2 FOREIGN KEY MemberGroup_SalesSegment_ibfk_2 (sales_segment_id) REFERENCES SalesSegmentGroup (id);
    """)
    op.execute("""
ALTER TABLE Product ADD CONSTRAINT Product_ibfk_1 FOREIGN KEY Product_ibfk_1 (sales_segment_id) REFERENCES SalesSegmentGroup (id);
    """)
    op.execute("""
ALTER TABLE PaymentDeliveryMethodPair ADD CONSTRAINT PaymentDeliveryMethodPair_ibfk_1 FOREIGN KEY PaymentDeliveryMethodPair_ibfk_1 (sales_segment_id) REFERENCES SalesSegmentGroup (id);
    """)
    op.execute("""
ALTER TABLE Lot ADD CONSTRAINT Lot_ibfk_2 FOREIGN KEY Lot_ibfk_2 (sales_segment_id) REFERENCES SalesSegmentGroup (id);
    """)
    op.execute("""
ALTER TABLE ticketing_carts ADD CONSTRAINT ticketing_carts_ibfk_5 FOREIGN KEY ticketing_carts_ibfk_5 (sales_segment_id) REFERENCES SalesSegmentGroup (id);
    """)
    op.execute("""
UNLOCK TABLES;
    """)

    # https://dev.ticketstar.jp/lodgeit/show/415/
    op.execute("""
CREATE TABLE SalesCondition (
    id bigint(20) PRIMARY KEY AUTO_INCREMENT,
    membergroup_id bigint(20) NOT NULL,
    sales_segment_id bigint(20) NOT NULL,
    UNIQUE KEY (membergroup_id, sales_segment_id),
    CONSTRAINT `SalesCondition_ibfk_1` FOREIGN KEY (`membergroup_id`) REFERENCES `MemberGroup` (`id`),
    CONSTRAINT `SalesCondition_ibfk_2` FOREIGN KEY (`sales_segment_id`) REFERENCES `SalesSegmentGroup` (`id`)
);
    """)
    op.execute("""
INSERT INTO SalesCondition SELECT id, membergroup_id, sales_segment_id FROM MemberGroup_SalesSegment;
    """)

def downgrade():

    # https://dev.ticketstar.jp/lodgeit/show/403/
    op.drop_constraint('SalesSegmentGroup_ibfk_1', 'SalesSegmentGroup', type="foreignkey")
    op.execute("""
ALTER TABLE MemberGroup_SalesSegment DROP FOREIGN KEY MemberGroup_SalesSegment_ibfk_2;
    """)
    op.execute("""
ALTER TABLE Product DROP FOREIGN KEY Product_ibfk_1;
    """)
    op.execute("""
ALTER TABLE PaymentDeliveryMethodPair DROP FOREIGN KEY PaymentDeliveryMethodPair_ibfk_1;
    """)
    op.execute("""
ALTER TABLE ticketing_carts DROP FOREIGN KEY ticketing_carts_ibfk_5;
    """)
    op.execute("""
ALTER TABLE Lot DROP FOREIGN KEY Lot_ibfk_2;
    """)
    op.execute("""
ALTER TABLE MemberGroup_SalesSegment ADD CONSTRAINT MemberGroup_SalesSegment_ibfk_2 FOREIGN KEY MemberGroup_SalesSegment_ibfk_2 (sales_segment_id) REFERENCES SalesSegment (id);
    """)
    op.execute("""
ALTER TABLE Product ADD CONSTRAINT Product_ibfk_1 FOREIGN KEY Product_ibfk_1 (sales_segment_id) REFERENCES SalesSegment (id);
    """)
    op.execute("""
ALTER TABLE PaymentDeliveryMethodPair ADD CONSTRAINT PaymentDeliveryMethodPair_ibfk_1 FOREIGN KEY PaymentDeliveryMethodPair_ibfk_1 (sales_segment_id) REFERENCES SalesSegment (id);
    """)
    op.execute("""
ALTER TABLE Lot ADD CONSTRAINT Lot_ibfk_2 FOREIGN KEY Lot_ibfk_2 (sales_segment_id) REFERENCES SalesSegment (id);
    """)
    op.execute("""
ALTER TABLE ticketing_carts ADD CONSTRAINT ticketing_carts_ibfk_5 FOREIGN KEY ticketing_carts_ibfk_5 (sales_segment_id) REFERENCES SalesSegment (id);
    """)
    op.execute("""
DROP TABLE `SalesCondition`, `SalesSegmentGroup`;
    """)

