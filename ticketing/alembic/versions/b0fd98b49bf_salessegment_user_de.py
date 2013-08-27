"""SalesSegment.user_default*

Revision ID: b0fd98b49bf
Revises: 571cbcc79a61
Create Date: 2013-08-23 18:32:31.930543

"""

# revision identifiers, used by Alembic.
revision = 'b0fd98b49bf'
down_revision = '571cbcc79a61'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column("SalesSegment", 
                  sa.Column("use_default_seat_choice", sa.Boolean))
    op.add_column("SalesSegment", 
                  sa.Column("use_default_public", sa.Boolean))
    op.add_column("SalesSegment", 
                  sa.Column("use_default_reporting", sa.Boolean))
    op.add_column("SalesSegment", 
                  sa.Column("use_default_payment_delivery_method_pairs", sa.Boolean))
    op.add_column("SalesSegment", 
                  sa.Column("use_default_start_at", sa.Boolean))
    op.add_column("SalesSegment", 
                  sa.Column("use_default_end_at", sa.Boolean))
    op.add_column("SalesSegment", 
                  sa.Column("use_default_upper_limit", sa.Boolean))
    op.add_column("SalesSegment", 
                  sa.Column("use_default_order_limit", sa.Boolean))
    op.add_column("SalesSegment", 
                  sa.Column("use_default_account_id", sa.Boolean))
    op.add_column("SalesSegment", 
                  sa.Column("use_default_margin_ratio", sa.Boolean))
    op.add_column("SalesSegment", 
                  sa.Column("use_default_refund_ratio", sa.Boolean))
    op.add_column("SalesSegment", 
                  sa.Column("use_default_printing_fee", sa.Boolean))
    op.add_column("SalesSegment", 
                  sa.Column("use_default_registration_fee", sa.Boolean))
    op.add_column("SalesSegment", 
                  sa.Column("use_default_auth3d_notice", sa.Boolean))


def downgrade():
    op.drop_column("SalesSegment", "use_default_seat_choice")
    op.drop_column("SalesSegment", "use_default_public")
    op.drop_column("SalesSegment", "use_default_reporting")
    op.drop_column("SalesSegment", "use_default_payment_delivery_method_pairs")
    op.drop_column("SalesSegment", "use_default_start_at")
    op.drop_column("SalesSegment", "use_default_end_at")
    op.drop_column("SalesSegment", "use_default_upper_limit")
    op.drop_column("SalesSegment", "use_default_order_limit")
    op.drop_column("SalesSegment", "use_default_account_id")
    op.drop_column("SalesSegment", "use_default_margin_ratio")
    op.drop_column("SalesSegment", "use_default_refund_ratio")
    op.drop_column("SalesSegment", "use_default_printing_fee")
    op.drop_column("SalesSegment", "use_default_registration_fee")
    op.drop_column("SalesSegment", "use_default_auth3d_notice")

