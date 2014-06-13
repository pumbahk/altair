"""alter table OrganizationSetting add column enable_mypage

Revision ID: 141f7ed1cda4
Revises: 2339a4ac4859
Create Date: 2014-06-13 11:54:53.524374

"""

# revision identifiers, used by Alembic.
revision = '141f7ed1cda4'
down_revision = '2339a4ac4859'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger

def upgrade():
    op.add_column('OrganizationSetting', sa.Column('enable_mypage', sa.Boolean(), nullable=False, default=False, server_default=text('0')))
    sql = """\
    UPDATE OrganizationSetting
    SET enable_mypage = 1
    WHERE organization_id in (15, 24, 36);
    """
    op.execute(sql)
def downgrade():
    op.drop_column('OrganizationSetting', 'enable_mypage')
