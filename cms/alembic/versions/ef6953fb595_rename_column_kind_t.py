"""rename column kind to tag

Revision ID: ef6953fb595
Revises: 141a155153a3
Create Date: 2013-02-04 17:38:58.352835

"""

# revision identifiers, used by Alembic.
revision = 'ef6953fb595'
down_revision = '141a155153a3'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    op.add_column('widget_promotion', sa.Column('tag_id', sa.Integer(), nullable=True))
    op.drop_column('widget_promotion', u'kind_id')


def downgrade():
    op.add_column('widget_promotion', sa.Column(u'kind_id', mysql.INTEGER(display_width=11), nullable=True))
    op.drop_column('widget_promotion', 'tag_id')
