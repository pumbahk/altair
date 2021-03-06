"""favorite word support

Revision ID: bf2ef09ab6c
Revises: 1cc638e76055
Create Date: 2016-04-14 10:47:36.417711

"""

# revision identifiers, used by Alembic.
revision = 'bf2ef09ab6c'
down_revision = '1cc638e76055'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text

Identifier = sa.BigInteger


def upgrade():
    op.create_table(
        'WordSubscription',
        sa.Column('id', Identifier(), primary_key=True),
        sa.Column('user_id', Identifier(), sa.ForeignKey('User.id'), nullable=False),
        sa.Column('word_id', Identifier(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        )

    op.add_column('OrganizationSetting', sa.Column('enable_word', sa.Boolean(), nullable=True, default=False))
    op.add_column('UserProfile', sa.Column('subscribe_word', sa.Boolean(), nullable=True, default=True))

def downgrade():
    op.drop_table('WordSubscription')
    op.drop_column('OrganizationSetting', 'enable_word')
    op.drop_column('UserProfile', 'subscribe_word')
