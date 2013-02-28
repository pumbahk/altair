"""create pagetype

Revision ID: 141a155153a3
Revises: 2584e1a420f6
Create Date: 2013-01-30 10:42:16.907883

"""

# revision identifiers, used by Alembic.
revision = '141a155153a3'
down_revision = '5a8a6eccba80'

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table('pagetype',
                    sa.Column('organization_id', sa.Integer(), nullable=True),
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(length=255), nullable=True, index=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.add_column('layout', sa.Column('pagetype_id', sa.Integer(), nullable=True))
    op.create_foreign_key("fk_layout_pagetype_id_to_pagetype_id", "layout", "pagetype", ["pagetype_id"], ["id"])
    op.add_column('page', sa.Column('pagetype_id', sa.Integer(), nullable=True))
    op.create_foreign_key("fk_page_pagetype_id_to_pagetype_id", "page", "pagetype", ["pagetype_id"], ["id"])
    op.add_column('pagesets', sa.Column('pagetype_id', sa.Integer(), nullable=True))
    op.create_foreign_key("fk_pagesets_pagetype_id_to_pagetype_id", "pagesets", "pagetype", ["pagetype_id"], ["id"])

    #data migration
    op.execute('INSERT INTO pagetype (name, organization_id) SELECT "event_detail" as name, id as organization_id FROM organization;')
    op.execute('INSERT INTO pagetype (name, organization_id) SELECT "static" as name, id as organization_id FROM organization;')
    op.execute('INSERT INTO pagetype (name, organization_id) SELECT "portal" as name, id as organization_id FROM organization;')

def downgrade():
    op.drop_constraint("fk_pagesets_pagetype_id_to_pagetype_id", "pagesets", type="foreignkey")
    op.drop_column('pagesets', 'pagetype_id')
    op.drop_constraint("fk_page_pagetype_id_to_pagetype_id", "page", type="foreignkey")
    op.drop_column('page', 'pagetype_id')
    op.drop_constraint("fk_layout_pagetype_id_to_pagetype_id", "layout", type="foreignkey")
    op.drop_column('layout', 'pagetype_id')
    op.drop_table('pagetype')
