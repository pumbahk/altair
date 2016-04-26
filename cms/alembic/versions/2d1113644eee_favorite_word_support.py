"""favorite word support

Revision ID: 2d1113644eee
Revises: d82cd501e6b
Create Date: 2016-04-14 10:53:34.311686

"""

# revision identifiers, used by Alembic.
revision = '2d1113644eee'
down_revision = 'd82cd501e6b'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text

def upgrade():
    op.create_table(
        'word',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('organization_id', sa.Integer(), sa.ForeignKey('organization.id'), nullable=False),
        sa.Column('type', sa.String(length=255), nullable=True),
        sa.Column('label', sa.String(length=255), nullable=False),
        sa.Column('label_kana', sa.String(length=255), nullable=True),
        sa.Column('description', sa.String(length=255), nullable=True),
        #sa.Column('link', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        )
    op.create_table(
        'word_search',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('word_id', sa.Integer(), sa.ForeignKey('word.id'), nullable=False),
        sa.Column('data', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        )
    op.create_table(
        'event_word',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('event_id', sa.Integer(), sa.ForeignKey('event.id'), nullable=False),
        sa.Column('word_id', sa.Integer(), sa.ForeignKey('word.id'), nullable=False),
        #sa.Column('sorting', Integer(), nullable=True),
        #sa.Column('subscribable', Integer(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        )
    op.create_table(
        'performance_word',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('performance_id', sa.Integer(), sa.ForeignKey('performance.id'), nullable=False),
        sa.Column('word_id', sa.Integer(), sa.ForeignKey('word.id'), nullable=False),
        #sa.Column('sorting', Integer(), nullable=True),
        #sa.Column('subscribable', Integer(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        )

def downgrade():
    op.drop_table('event_word')
    op.drop_table('performance_word')
    op.drop_table('word_search')
    op.drop_table('word')
