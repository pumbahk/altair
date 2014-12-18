"""add indexes to tables related to multicheckout, esp. of OrderNo

Revision ID: 83224a82fa6
Revises: 7657f6f6b68
Create Date: 2014-12-19 02:20:15.572264

"""

# revision identifiers, used by Alembic.
revision = '83224a82fa6'
down_revision = '7657f6f6b68'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    # https://redmine.ticketstar.jp/issues/10493
    op.execute("""
ALTER TABLE `ticketing`.`multicheckout_order_status` ADD INDEX `ix_Storecd_Status` (`Storecd`,`Status`);
    """)
    op.execute("""
ALTER TABLE `ticketing`.`multicheckout_inquiry_response_card` ADD INDEX `ix_OrderNo` (`OrderNo`);
    """)
    op.execute("""
ALTER TABLE `ticketing`.`multicheckout_response_card` ADD INDEX `ix_OrderNo` (`OrderNo`);
    """)
    op.execute("""
ALTER TABLE `ticketing`.`secure3d_req_auth_response` ADD INDEX `ix_OrderNo` (`OrderNo`);
    """)
    op.execute("""
ALTER TABLE `ticketing`.`secure3d_req_enrol_response ` ADD INDEX `ix_OrderNo` (`OrderNo`);
    """)

def downgrade():
    op.execute("""
ALTER TABLE `ticketing`.`multicheckout_order_status` DROP INDEX `ix_Storecd_Status`;
    """)
    op.execute("""
ALTER TABLE `ticketing`.`multicheckout_inquiry_response_card` DROP INDEX `ix_OrderNo`;
    """)
    op.execute("""
ALTER TABLE `ticketing`.`multicheckout_response_card` DROP INDEX `ix_OrderNo`;
    """)
    op.execute("""
ALTER TABLE `ticketing`.`secure3d_req_auth_response` DROP INDEX `ix_OrderNo`;
    """)
    op.execute("""
ALTER TABLE `ticketing`.`secure3d_req_enrol_response ` DROP INDEX `ix_OrderNo`;
    """)
