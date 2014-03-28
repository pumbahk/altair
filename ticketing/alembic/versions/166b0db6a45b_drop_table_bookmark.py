"""drop table Bookmark

Revision ID: 166b0db6a45b
Revises: 1964706e096b
Create Date: 2014-03-17 20:26:00.103305

"""

# revision identifiers, used by Alembic.
revision = '166b0db6a45b'
down_revision = '1964706e096b'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.drop_table('Bookmark')

def downgrade():
    op.create_table('Bookmark',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('url', sa.String(length=1024), nullable=True),
        sa.Column('organization_id', Identifier(), nullable=True),
        sa.Column('status', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['Organization.id'], 'Bookmark_ibfk_1'),
        sa.PrimaryKeyConstraint('id')
        )
