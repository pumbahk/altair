"""static page also has pageset

Revision ID: 1ac7a5654384
Revises: 512e091d8fc6
Create Date: 2013-05-17 12:18:33.969481

"""

# revision identifiers, used by Alembic.
revision = '1ac7a5654384'
down_revision = '142cf4285441'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    op.create_table('static_pagesets',
                    sa.Column('organization_id', sa.Integer(), nullable=True),
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.Unicode(length=255), nullable=True),
                    sa.Column('version_counter', sa.Integer(), nullable=True),
                    sa.Column('url', sa.String(length=255), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.Column('pagetype_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['pagetype_id'], ['pagetype.id'], ),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('url', 'organization_id')
                    )
    op.add_column('static_pages', sa.Column('pageset_id', sa.Integer(), nullable=True))
    for i in range(10): #slack-off
        op.execute('''INSERT INTO static_pagesets (name,version_counter,url,organization_id,created_at,updated_at,pagetype_id) 
  (SELECT name, 0, name, organization_id, now(), now(), (select id from pagetype where organization_id = {0} and name = "static")
  FROM static_pages where organization_id = {0});'''.format(i))
    op.execute('''UPDATE static_pagesets as ps join static_pages as p on ps.organization_id = p.organization_id and ps.name = p.name set p.pageset_id = ps.id;''')


def downgrade():
    op.drop_table('static_pagesets')
    op.drop_column('static_pages', 'pageset_id')

