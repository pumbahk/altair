"""Create OAuthServiceProvider

Revision ID: 38a51a4056bf
Revises: 2d0967f9ca06
Create Date: 2016-11-02 17:15:00.906649

"""

# revision identifiers, used by Alembic.
revision = '38a51a4056bf'
down_revision = '2d0967f9ca06'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
     op.create_table(
        'OAuthServiceProvider',
        sa.Column('id', Identifier, autoincrement=True, primary_key=True, nullable=False),
        sa.Column('name', sa.Unicode(32), nullable=False),
        sa.Column('display_name', sa.Unicode(255), nullable=False),
        sa.Column('auth_type', sa.Unicode(64), nullable=False),
        sa.Column('endpoint_base', sa.Unicode(255), nullable=False),
        sa.Column('consumer_key', sa.Unicode(255), nullable=False),
        sa.Column('consumer_secret', sa.Unicode(255), nullable=False),
        sa.Column('scope', sa.Unicode(255), nullable=True, default=u''),
        sa.Column('organization_id', Identifier, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=text(u'CURRENT_TIMESTAMP()'))
        )

def downgrade():
    op.drop_table('OAuthServiceProvider')
