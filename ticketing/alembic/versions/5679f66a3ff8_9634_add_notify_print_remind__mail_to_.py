"""#9634 add notify_print_remind__mail to OrganizationSetting

Revision ID: 5679f66a3ff8
Revises: 585612b4453b
Create Date: 2015-07-13 15:01:10.333655

"""

# revision identifiers, used by Alembic.
revision = '5679f66a3ff8'
down_revision = '585612b4453b'

from alembic import op
import sqlalchemy as sa

Identifier = sa.BigInteger


def upgrade():
    op.add_column('OrganizationSetting', sa.Column('notify_print_remind_mail', sa.Boolean(), nullable=False, default=False, server_default='0'))

def downgrade():
    op.drop_column('OrganizationSetting', 'notify_print_remind_mail')
