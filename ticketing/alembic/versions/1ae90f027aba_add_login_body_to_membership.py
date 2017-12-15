"""add login body to Membership

Revision ID: 1ae90f027aba
Revises: 23db677af8c6
Create Date: 2017-11-29 19:37:01.164012

"""

# revision identifiers, used by Alembic.
revision = '1ae90f027aba'
down_revision = '23db677af8c6'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf
from sqlalchemy.dialects.mysql import MEDIUMTEXT

Identifier = sa.BigInteger


def upgrade():
    op.add_column(u'Membership', sa.Column(u'enable_login_body', sa.Boolean, default=False, server_default='0'))
    op.add_column(u'Membership', sa.Column(u'login_body_pc', MEDIUMTEXT(charset='utf8'), nullable=True))
    op.add_column(u'Membership', sa.Column(u'login_body_smartphone', MEDIUMTEXT(charset='utf8'), nullable=True))
    op.add_column(u'Membership', sa.Column(u'login_body_mobile', MEDIUMTEXT(charset='utf8'), nullable=True))
    op.add_column(u'Membership', sa.Column(u'login_body_error_message', sa.UnicodeText, nullable=True))

def downgrade():
    op.drop_column('Membership', 'enable_login_body')
    op.drop_column('Membership', 'login_body_pc')
    op.drop_column('Membership', 'login_body_smartphone')
    op.drop_column('Membership', 'login_body_mobile')
    op.drop_column('Membership', 'login_body_error_message')
