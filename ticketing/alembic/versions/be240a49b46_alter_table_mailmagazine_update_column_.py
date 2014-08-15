"""alter table MailMagazine update column status

Revision ID: be240a49b46
Revises: 164ba9781aae
Create Date: 2014-08-11 15:05:47.336590

"""

# revision identifiers, used by Alembic.
revision = 'be240a49b46'
down_revision = '164ba9781aae'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.drop_column(u'MailMagazine', u'status')
    op.add_column(u'MailMagazine', sa.Column(u'status', sa.Boolean, default=True, server_default='1'))

def downgrade():
    op.drop_column(u'MailMagazine', u'status')
    op.add_column(u'MailMagazine', sa.Column('status', sa.Integer(), nullable=True))
