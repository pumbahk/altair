"""add talbe Word

Revision ID: 2c98f57e91b2
Revises: 46d8b483857d
Create Date: 2020-09-11 11:54:21.320202

"""

# revision identifiers, used by Alembic.
revision = '2c98f57e91b2'
down_revision = '46d8b483857d'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table(
        'Word',
        sa.Column('id', Identifier, primary_key=True),
        sa.Column('type', sa.String(length=255), nullable=True, default=""),
        sa.Column('label', sa.String(length=255), nullable=True, default=""),
        sa.Column('label_kana', sa.String(length=255), nullable=True, default=""),
        sa.Column('description', sa.String(length=255), nullable=True, default=""),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
    )


def downgrade():
    op.drop_table('Word')
