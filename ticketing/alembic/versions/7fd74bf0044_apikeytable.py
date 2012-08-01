"""apikeytable

Revision ID: 7fd74bf0044
Revises: 3b808f24eb38
Create Date: 2012-07-28 04:01:14.567187

"""

# revision identifiers, used by Alembic.
revision = '7fd74bf0044'
down_revision = '3b808f24eb38'

from alembic import op
import sqlalchemy as sa

Identifier = sa.BigInteger

def upgrade():
    op.create_table('APIKey',
        sa.Column('id', Identifier(), nullable=False, autoincrement=True),
        sa.Column('expire_at', sa.DateTime(), nullable=True),
        sa.Column('apikey', sa.String(length=255), nullable=False, unique=True)
        )

def downgrade():
    op.drop_table('APIKey')
