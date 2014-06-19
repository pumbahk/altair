"""is_send_remind_mail

Revision ID: 145a56bd800c
Revises: e6d2bfcc31e
Create Date: 2014-06-19 09:51:08.427018

"""

# revision identifiers, used by Alembic.
revision = '145a56bd800c'
down_revision = 'e6d2bfcc31e'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('OrganizationSetting', sa.Column('notify_remind_mail', sa.Boolean(), nullable=False, default=False))

def downgrade():
    op.drop_column('OrganizationSetting', 'notify_remind_mail')
