"""alter table ReportSetting modify column time

Revision ID: 2e1379ff8b2c
Revises: 49bb9c608cc2
Create Date: 2014-04-21 16:44:34.752112

"""

# revision identifiers, used by Alembic.
revision = '2e1379ff8b2c'
down_revision = '49bb9c608cc2'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger



def upgrade():
    op.execute('UPDATE ReportSetting SET time = CONCAT(LPAD(time, 2, "0"), "10")')

def downgrade():
    op.execute('UPDATE ReportSetting SET time = TRIM("0" FROM SUBSTR(time, 1, 2))')
