"""add live streaming table and column

Revision ID: 4db0d62b9fd5
Revises: 2e45c8b61b2d
Create Date: 2020-06-04 11:39:55.869421

"""

# revision identifiers, used by Alembic.
revision = '4db0d62b9fd5'
down_revision = '2e45c8b61b2d'

import sqlalchemy as sa

Identifier = sa.BigInteger

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf
from sqlalchemy.dialects.mysql import TEXT

Identifier = sa.BigInteger


def upgrade():
    op.add_column('OrganizationSetting',
                  sa.Column('enable_live_performance', sa.Boolean(), nullable=False, default=False))

    op.create_table(
        'LivePerformanceSetting',
        sa.Column('id', Identifier, primary_key=True),
        sa.Column('performance_id', Identifier(), nullable=False),
        sa.Column('live_code', TEXT(charset='utf8'), nullable=True),
        sa.Column('label', sa.Unicode(length=255), nullable=True),
        sa.Column('description', TEXT(charset='utf8'), nullable=True),
        sa.Column('publish_start_at', sa.DateTime(), nullable=False),
        sa.Column('publish_end_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['performance_id'], ['Performance.id'], 'LivePerformanceSetting_ibfk_1'),
        sa.UniqueConstraint('performance_id')
    )


def downgrade():
    op.drop_table('LivePerformanceSetting')
    op.drop_column('OrganizationSetting', 'enable_live_performance')
