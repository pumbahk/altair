"""add easy_id column to UserCredential

Revision ID: 31b7c716d9bb
Revises: 4b041d4e9b85
Create Date: 2018-11-09 13:54:30.402816

"""

# revision identifiers, used by Alembic.
revision = '31b7c716d9bb'
down_revision = '4b041d4e9b85'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('UserCredential', sa.Column('easy_id', sa.Unicode(length=16), index=True))
    op.create_index('easy_id', 'UserCredential', ['easy_id'])


def downgrade():
    op.drop_column('UserCredential', 'easy_id')
