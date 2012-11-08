"""add column Order.branch_no

Revision ID: 54d62937d132
Revises: 2d3bab513d5
Create Date: 2012-11-08 10:33:02.138176

"""

# revision identifiers, used by Alembic.
revision = '54d62937d132'
down_revision = '2d3bab513d5'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.execute("ALTER TABLE `Order` ADD COLUMN branch_no int(11) NOT NULL DEFAULT '1';")
    op.execute("UPDATE `Order` SET branch_no=2 WHERE id in (3371, 3375)")
    op.execute("ALTER TABLE `Order` ADD UNIQUE ix_Order_order_no_branch_no (order_no, branch_no);")

def downgrade():
    op.execute("ALTER TABLE `Order` DROP INDEX ix_Order_order_no_branch_no;")
    op.execute("ALTER TABLE `Order` DROP COLUMN branch_no;")

