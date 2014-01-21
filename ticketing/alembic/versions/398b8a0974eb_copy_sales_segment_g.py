# -*- coding:utf-8 -*-
"""add SalesSegment table and sales_segment_id columns.

Revision ID: 398b8a0974eb
Revises: 317d5e17c201
Create Date: 2013-01-23 19:08:52.673436

only schema
"""

# revision identifiers, used by Alembic.
revision = '398b8a0974eb'
down_revision = '333d0bcd2f83'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    # SalesSegmentGroupの残骸を削除
    op.drop_table("SalesSegment")

    # create SalesSegment
    op.create_table("SalesSegment",
    sa.Column("id", Identifier, primary_key=True),
    sa.Column("start_at", sa.DateTime),
    sa.Column("end_at", sa.DateTime),
    sa.Column("upper_limit", sa.Integer),
    sa.Column("seat_choice", sa.Boolean, default=True),
    sa.Column("public", sa.Boolean, default=True),
    sa.Column("performance_id", Identifier, sa.ForeignKey('Performance.id')),
    sa.Column("sales_segment_group_id", Identifier, sa.ForeignKey("SalesSegmentGroup.id")),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
    sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
    )

    op.execute(""" ALTER TABLE MemberGroup_SalesSegment ADD COLUMN sales_segment_id BIGINT; """)
    op.execute(""" ALTER TABLE MemberGroup_SalesSegment ADD CONSTRAINT MemberGroup_SalesSegment_ibfk_3 FOREIGN KEY (sales_segment_id) REFERENCES SalesSegment (id); """)
    op.execute(""" ALTER TABLE Product DROP FOREIGN KEY Product_ibfk_1; """)
    op.execute(""" ALTER TABLE Product DROP INDEX Product_ibfk_1; """)
    op.execute(""" ALTER TABLE Product ADD COLUMN sales_segment_id BIGINT; """)
    op.execute(""" ALTER TABLE Product ADD CONSTRAINT Product_ibfk_1 FOREIGN KEY (sales_segment_group_id) REFERENCES SalesSegmentGroup (id); """)
    op.execute(""" ALTER TABLE Product ADD CONSTRAINT Product_ibfk_3 FOREIGN KEY (sales_segment_id) REFERENCES SalesSegment (id); """)
    op.execute(""" ALTER TABLE PaymentDeliveryMethodPair ADD COLUMN sales_segment_id BIGINT; """)
    op.execute(""" ALTER TABLE PaymentDeliveryMethodPair ADD CONSTRAINT PaymentDeliveryMethodPair_ibfk_4 FOREIGN KEY (sales_segment_id) REFERENCES SalesSegment (id); """)
    op.execute(""" ALTER TABLE Lot ADD COLUMN sales_segment_id BIGINT; """)
    op.execute(""" ALTER TABLE Lot ADD CONSTRAINT Lot_ibfk_3 FOREIGN KEY (sales_segment_id) REFERENCES SalesSegment (id); """)

def downgrade():

    op.execute(""" ALTER TABLE MemberGroup_SalesSegment DROP FOREIGN KEY MemberGroup_SalesSegment_ibfk_3; """)
    op.execute(""" ALTER TABLE MemberGroup_SalesSegment DROP COLUMN sales_segment_id; """)
    op.execute(""" ALTER TABLE Product DROP FOREIGN KEY Product_ibfk_3; """)
    op.execute(""" ALTER TABLE Product DROP COLUMN sales_segment_id; """)
    op.execute(""" ALTER TABLE Product DROP CONSTRAINT Product_ibfk_1; """)
    op.execute(""" ALTER TABLE Product DROP INDEX sales_segment_group_id; """)
    op.execute(""" ALTER TABLE Product ADD CONSTRAINT Product_ibfk_1 FOREIGN KEY (sales_segment_group_id) REFERENCES SalesSegmentGroup (id); """)
    op.execute(""" ALTER TABLE PaymentDeliveryMethodPair DROP FOREIGN KEY PaymentDeliveryMethodPair_ibfk_4; """)
    op.execute(""" ALTER TABLE PaymentDeliveryMethodPair DROP COLUMN sales_segment_id; """)
    op.execute(""" ALTER TABLE Lot DROP FOREIGN KEY Lot_ibfk_3; """)
    op.execute(""" ALTER TABLE Lot DROP COLUMN sales_segment_id; """)

