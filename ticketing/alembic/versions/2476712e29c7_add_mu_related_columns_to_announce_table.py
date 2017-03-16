"""add mu related columns to Announce table

Revision ID: 2476712e29c7
Revises: adb5ee95d7c
Create Date: 2017-01-24 14:11:52.816936

"""

# revision identifiers, used by Alembic.
revision = '2476712e29c7'
down_revision = 'adb5ee95d7c'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf


def upgrade():
    op.add_column('Announcement', sa.Column('mu_trans_id', sa.String(length=255), nullable=True, index=True))
    op.add_column('Announcement', sa.Column('mu_status', sa.String(length=255), nullable=True))
    op.add_column('Announcement', sa.Column('mu_result', sa.String(length=255), nullable=True))
    op.add_column('Announcement', sa.Column('mu_accepted_count', sa.Integer, nullable=True))
    op.add_column('Announcement', sa.Column('mu_sent_count', sa.Integer, nullable=True))


def downgrade():
    op.drop_column('Announcement', 'mu_trans_id')
    op.drop_column('Announcement', 'mu_status')
    op.drop_column('Announcement', 'mu_result')
    op.drop_column('Announcement', 'mu_accepted_count')
    op.drop_column('Announcement', 'mu_sent_count')
