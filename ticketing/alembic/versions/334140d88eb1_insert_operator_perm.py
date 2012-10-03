"""insert operator permission

Revision ID: 334140d88eb1
Revises: 358718d4a203
Create Date: 2012-09-25 21:25:01.568171

"""

# revision identifiers, used by Alembic.
revision = '334140d88eb1'
down_revision = '358718d4a203'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.execute("INSERT INTO OperatorRole (id, name, status, created_at, updated_at) VALUES (3, 'operator', 1, now(), now())")
    op.execute("INSERT INTO Permission (id, operator_role_id, category_name, permit) VALUES (37, 3, 'event_viewer', 1)")
    op.execute("INSERT INTO Permission (id, operator_role_id, category_name, permit) VALUES (38, 1, 'sales_counter', 1)")
    op.execute("INSERT INTO Permission (id, operator_role_id, category_name, permit) VALUES (39, 2, 'sales_counter', 1)")
    op.execute("INSERT INTO Permission (id, operator_role_id, category_name, permit) VALUES (40, 3, 'sales_counter', 1)")

def downgrade():
    op.execute("DELETE FROM Permission WHERE id IN (37, 38, 39, 40);")
    op.execute("DELETE FROM OperatorRole WHERE id=3;")
