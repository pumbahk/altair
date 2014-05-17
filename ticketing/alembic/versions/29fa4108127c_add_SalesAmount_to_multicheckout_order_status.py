"""add_SalesAmount_to_multicheckout_order_status

Revision ID: 29fa4108127c
Revises: 2c6b02262439
Create Date: 2014-04-21 04:03:04.170342

"""

# revision identifiers, used by Alembic.
revision = '29fa4108127c'
down_revision = '2c6b02262439'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('multicheckout_order_status', sa.Column('SalesAmount', sa.Integer(), nullable=True))
    op.execute("""UPDATE multicheckout_order_status JOIN (SELECT multicheckout_inquiry_response_card.OrderNo, MIN(multicheckout_inquiry_response_card.SalesAmount) minimum_sales_amount, `Order`.total_amount FROM multicheckout_inquiry_response_card LEFT JOIN `Order` ON multicheckout_inquiry_response_card.OrderNo=`Order`.order_no GROUP BY multicheckout_inquiry_response_card.OrderNo) _ ON multicheckout_order_status.OrderNo=_.OrderNo SET multicheckout_order_status.SalesAmount=IF(_.minimum_sales_amount IS NULL, _.total_amount, _.minimum_sales_amount)""")

def downgrade():
    op.drop_column('multicheckout_order_status', 'SalesAmount')
