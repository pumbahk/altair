"""renewal topic

Revision ID: 46438f663254
Revises: ef6953fb595
Create Date: 2013-02-04 18:46:57.256037

"""

# revision identifiers, used by Alembic.
revision = '46438f663254'
down_revision = 'ef6953fb595'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    op.create_table('widget_topcontent',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('display_type', sa.Unicode(length=255), nullable=True),
                    sa.Column('display_count', sa.Integer(), nullable=True),
                    sa.Column('tag_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['id'], ['widget.id'], ),
                    sa.ForeignKeyConstraint(['tag_id'], ['topcontenttag.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.add_column('widget_topic', sa.Column('display_type', sa.Unicode(length=255), nullable=True))
    op.add_column('widget_topic', sa.Column('tag_id', sa.Integer(), nullable=True))
    op.drop_column('widget_topic', u'kind')
    op.drop_column('widget_topic', u'display_event')
    op.drop_column('widget_topic', u'topic_type')
    op.drop_column('widget_topic', u'display_page')
    op.drop_column('widget_topic', u'display_global')
    op.drop_column('widget_topic', u'subkind')

def downgrade():
    op.add_column('widget_topic', sa.Column(u'subkind', mysql.VARCHAR(length=255), nullable=True))
    op.add_column('widget_topic', sa.Column(u'display_global', mysql.TINYINT(display_width=1), nullable=True))
    op.add_column('widget_topic', sa.Column(u'display_page', mysql.TINYINT(display_width=1), nullable=True))
    op.add_column('widget_topic', sa.Column(u'topic_type', mysql.VARCHAR(length=255), nullable=True))
    op.add_column('widget_topic', sa.Column(u'display_event', mysql.TINYINT(display_width=1), nullable=True))
    op.add_column('widget_topic', sa.Column(u'kind', mysql.VARCHAR(length=255), nullable=True))
    op.drop_column('widget_topic', 'tag_id')
    op.drop_column('widget_topic', 'display_type')
    op.drop_table('widget_topcontent')
