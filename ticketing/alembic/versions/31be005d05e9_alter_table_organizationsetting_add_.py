"""alter table OrganizationSetting add column recaptcha

Revision ID: 31be005d05e9
Revises: 3b9d24020871
Create Date: 2017-07-31 18:10:33.221244

"""

# revision identifiers, used by Alembic.
revision = '31be005d05e9'
down_revision = '3b9d24020871'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('OrganizationSetting', sa.Column('recaptcha', sa.Boolean(), nullable=False, default=False, server_default=text('0')))

def downgrade():
    op.drop_column('OrganizationSetting', 'recaptcha')
