"""membership..etc logically deleted

Revision ID: 38c552ae855d
Revises: 4b2d4985a0b0
Create Date: 2012-10-16 11:21:18.922314

"""

# revision identifiers, used by Alembic.
revision = '38c552ae855d'
down_revision = '4b2d4985a0b0'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger
from sqlalchemy.dialects import mysql

def upgrade():
    op.add_column(u'MemberGroup', sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True))
    op.add_column(u'Membership', sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True))
    op.add_column(u'User', sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True))
    op.add_column(u'UserCredential', sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True))
    op.add_column(u'UserProfile', sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True))
    op.add_column(u'MailSubscription', sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True))

def downgrade():
    op.drop_column(u'UserProfile', 'deleted_at')
    op.drop_column(u'UserCredential', 'deleted_at')
    op.drop_column(u'User', 'deleted_at')
    op.drop_column(u'Membership', 'deleted_at')
    op.drop_column(u'MemberGroup', 'deleted_at')
    op.drop_column(u'MailSubscription', 'deleted_at')
