"""insert permissions

Revision ID: 825b50ada09
Revises: 57294f6a2196
Create Date: 2012-09-13 22:09:07.852860

"""

# revision identifiers, used by Alembic.
revision = '825b50ada09'
down_revision = '57294f6a2196'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.execute("insert into Permission (id, operator_role_id, category_name, permit) values (29, 1, 'master_viewer', 1)")
    op.execute("insert into Permission (id, operator_role_id, category_name, permit) values (30, 1, 'master_editor', 1)")
    op.execute("insert into Permission (id, operator_role_id, category_name, permit) values (31, 1, 'sales_viewer', 1)")
    op.execute("insert into Permission (id, operator_role_id, category_name, permit) values (32, 1, 'sales_editor', 1)")
    op.execute("insert into Permission (id, operator_role_id, category_name, permit) values (33, 2, 'master_viewer', 1)")
    op.execute("insert into Permission (id, operator_role_id, category_name, permit) values (34, 2, 'master_editor', 1)")
    op.execute("insert into Permission (id, operator_role_id, category_name, permit) values (35, 2, 'sales_viewer', 1)")
    op.execute("insert into Permission (id, operator_role_id, category_name, permit) values (36, 2, 'sales_editor', 1)")
    op.execute("update OperatorRole_Operator set operator_role_id = 2 where operator_id != 1")

def downgrade():
    pass
