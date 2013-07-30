"""extend page access key

Revision ID: 143c45be235a
Revises: 4df15f221e78
Create Date: 2013-07-12 11:17:45.171499

"""

# revision identifiers, used by Alembic.
revision = '143c45be235a'
down_revision = '34639b5a1e44'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    op.add_column('page_accesskeys', sa.Column('event_id', sa.Integer(), nullable=True))
    op.add_column('page_accesskeys', sa.Column('operator_id', sa.Integer(), nullable=True))
    op.add_column('page_accesskeys', sa.Column('scope', sa.String(length=16), nullable=False))
    op.create_foreign_key("fk_page_accesskeys_event_id_to_event_id", "page_accesskeys", "event", ["event_id"], ["id"])
    op.create_foreign_key("fk_page_accesskeys_operator_id_to_operator_id", "page_accesskeys", "operator", ["operator_id"], ["id"])
    op.execute('update page_accesskeys set scope = "onepage";')
    op.execute('update (page as p join page_accesskeys as k on p.id = k.id) set k.organization_id = p.organization_id  where k.page_id is not NULL;')

def downgrade():
    op.drop_column('page_accesskeys', 'scope')
    op.drop_constraint("fk_page_accesskeys_operator_id_to_operator_id", "page_accesskeys", type="foreignkey")
    op.drop_column('page_accesskeys', 'operator_id')
    op.drop_constraint("fk_page_accesskeys_event_id_to_event_id", "page_accesskeys", type="foreignkey")
    op.drop_column('page_accesskeys', 'event_id')
