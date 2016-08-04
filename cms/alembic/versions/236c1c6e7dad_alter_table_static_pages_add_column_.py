"""alter table static_pages add column description, keywords

Revision ID: 236c1c6e7dad
Revises: 2d1113644eee
Create Date: 2016-08-01 14:24:03.539339

"""

# revision identifiers, used by Alembic.
revision = '236c1c6e7dad'
down_revision = '2d1113644eee'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import MEDIUMTEXT


def upgrade():
    op.add_column('static_pages', sa.Column('description', type_=MEDIUMTEXT(charset='utf8'), nullable=True))
    op.add_column('static_pages', sa.Column('keywords', type_=MEDIUMTEXT(charset='utf8'), nullable=True))

def downgrade():
    op.drop_column('static_pages', 'keywords')
    op.drop_column('static_pages', 'description')

