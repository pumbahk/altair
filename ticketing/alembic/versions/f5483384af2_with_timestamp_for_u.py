"""with_timestamp_for_user_models

Revision ID: f5483384af2
Revises: 120a39674247
Create Date: 2012-08-10 14:45:05.499857

"""

# revision identifiers, used by Alembic.
revision = 'f5483384af2'
down_revision = '120a39674247'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

def apply(table):
    op.alter_column(table, 'created_at', nullable=False, server_default=sqlf.current_timestamp(), type_=sa.TIMESTAMP(), existing_type=sa.DateTime(), existing_nullable=True)
    op.alter_column(table, 'updated_at', nullable=False, server_default=text('0'), type_=sa.TIMESTAMP(), existing_type=sa.DateTime(), existing_nullable=True)

def unapply(table):
    op.alter_column(table, 'created_at', nullable=True, type_=sa.DateTime(), server_default=text('NULL'), existing_type=sa.DateTime(), existing_server_default=sqlf.current_timestamp(), existing_nullable=False)
    op.alter_column(table, 'updated_at', nullable=True, type_=sa.DateTime(), server_default=text('NULL'), existing_type=sa.DateTime(), existing_server_default=text('0'), existing_nullable=False)

tables = [
    'User',
    'UserProfile',
    'UserCredential',
    'UserPointAccount',
    'MailMagazine',
    'MailSubscription',
    'MemberShip'
    ]

def upgrade():
    for table in tables:
        apply(table)

def downgrade():
    for table in tables:
        unapply(table)
