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
    op.execute("insert into OperatorRole (id, name, status, created_at, updated_at) values (3, 'operator', 1, now(), now())")
    op.execute("insert into Permission (id, operator_role_id, category_name, permit) values (37, 3, 'event_viewer', 1)")
    op.execute("insert into Permission (id, operator_role_id, category_name, permit) values (38, 1, 'sales_counter', 1)")
    op.execute("insert into Permission (id, operator_role_id, category_name, permit) values (39, 2, 'sales_counter', 1)")
    op.execute("insert into Permission (id, operator_role_id, category_name, permit) values (40, 3, 'sales_counter', 1)")

def downgrade():
    pass
