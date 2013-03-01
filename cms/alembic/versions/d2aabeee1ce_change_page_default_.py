"""change page default info

Revision ID: d2aabeee1ce
Revises: e964109e7bd
Create Date: 2013-02-26 18:21:22.101003

"""

# revision identifiers, used by Alembic.
revision = 'd2aabeee1ce'
down_revision = 'e964109e7bd'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    op.drop_constraint("fk_page_default_info_pageset_id_to_pagesets_id", "page_default_info", type="foreignkey")
    op.drop_index("fk_page_default_info_pageset_id_to_pagesets_id", "page_default_info")
    op.drop_column('page_default_info', u'url_fmt')
    op.drop_column('page_default_info', u'title_fmt')
    op.drop_column('page_default_info', u'pageset_id')

    op.add_column('page_default_info', sa.Column('url_prefix', sa.Unicode(length=255), nullable=True))
    op.add_column('page_default_info', sa.Column('organization_id', sa.Integer(), nullable=True))
    op.add_column('page_default_info', sa.Column('pagetype_id', sa.Integer(), nullable=True))
    op.add_column('page_default_info', sa.Column('title_prefix', sa.Unicode(length=255), nullable=True))
    op.create_foreign_key("fk_page_default_info_pagetype_id_to_pagetype_id", "page_default_info", "pagetype", ["pagetype_id"], ["id"])

def downgrade():
    op.drop_constraint("fk_page_default_info_pagetype_id_to_pagetype_id", "page_default_info", type="foreignkey")
    op.drop_index("fk_page_default_info_pagetype_id_to_pagetype_id", "page_default_info")
    op.add_column('page_default_info', sa.Column(u'pageset_id', mysql.INTEGER(display_width=11), nullable=True))
    op.add_column('page_default_info', sa.Column(u'title_fmt', mysql.VARCHAR(length=255), nullable=True))
    op.add_column('page_default_info', sa.Column(u'url_fmt', mysql.VARCHAR(length=255), nullable=True))
    op.create_foreign_key("fk_page_default_info_pageset_id_to_pagesets_id", "page_default_info", "pagesets", ["pageset_id"], ["id"])
    op.drop_column('page_default_info', 'title_prefix')
    op.drop_column('page_default_info', 'pagetype_id')
    op.drop_column('page_default_info', 'organization_id')
    op.drop_column('page_default_info', 'url_prefix')
