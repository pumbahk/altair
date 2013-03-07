"""default OrganizationSetting

Revision ID: 3e251dc4cbb7
Revises: 40d78cfd6809
Create Date: 2013-03-07 09:42:32.162338

"""

# revision identifiers, used by Alembic.
revision = '3e251dc4cbb7'
down_revision = '40d78cfd6809'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf
from sqlalchemy.sql import table, column

Identifier = sa.BigInteger


def upgrade():
    sql = ("insert into OrganizationSetting "
           "(organization_id, auth_type, name) "
           "select id as organization_id,'fc_auth' as auth_type,'default' as name "
           "from Organization "
           "where (id,'default') not in (select organization_id, name from OrganizationSetting); ")
    op.execute(sql)
    
def downgrade():
    op.execute("delete from OrganizationSetting where name = 'default'")
