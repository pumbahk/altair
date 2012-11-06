"""add organization short_name

Revision ID: 43c6379bbc86
Revises: 7a73f2f85e4
Create Date: 2012-11-06 13:55:36.442278

"""

# revision identifiers, used by Alembic.
revision = '43c6379bbc86'
down_revision = '7a73f2f85e4'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(u'organization', sa.Column('short_name', sa.String(length=32), nullable=False, index=True))
    op.add_column(u"organization",  sa.Column("use_full_usersite",  sa.Boolean(), default=False))

def downgrade():
    op.drop_column(u'organization', 'short_name')
    op.drop_column(u'organization', 'use_full_usersite')
