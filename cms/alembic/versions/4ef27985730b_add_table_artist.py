"""add table artist

Revision ID: 4ef27985730b
Revises: 14cecaa8695f
Create Date: 2019-06-17 11:37:34.735847

"""

# revision identifiers, used by Alembic.
revision = '4ef27985730b'
down_revision = '14cecaa8695f'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import MEDIUMTEXT


old_options = (
'event_create', 'event_read', 'event_update', 'event_delete', 'topic_create', 'topic_read', 'topic_update',
'topic_delete',
'topcontent_create', 'topcontent_read', 'topcontent_update', 'topcontent_delete', 'ticket_create', 'ticket_read',
'ticket_update',
'ticket_delete', 'magazine_create', 'magazine_read', 'magazine_update', 'magazine_delete', 'asset_create', 'asset_read',
'asset_update',
'asset_delete', 'page_create', 'page_read', 'page_update', 'page_delete', 'tag_create', 'tag_read', 'tag_update',
'tag_delete', 'category_create',
'category_read', 'category_update', 'category_delete', 'promotion_create', 'promotion_read', 'promotion_update',
'promotion_delete',
'promotion_unit_create', 'promotion_unit_read', 'promotion_unit_update', 'promotion_unit_delete', 'sale_create',
'sale_read', 'sale_update',
'sale_delete', 'performance_create', 'performance_read', 'performance_update', 'performance_delete', 'layout_create',
'layout_read', 'layout_update',
'layout_delete', 'operator_create', 'operator_read', 'operator_update', 'operator_delete', 'hotword_create',
'hotword_read', 'hotword_update', 'hotword_delete',
'pagedefaultinfo_create', 'pagedefaultinfo_read', 'pagedefaultinfo_update', 'pagedefaultinfo_delete',
'important_page_create', 'important_page_read', 'organization_create', 'host_create')

new_options = (old_options + ('artist_create', 'artist_read', 'artist_update', 'artist_delete'))

old_type = sa.Enum(*old_options, name='name')
new_type = sa.Enum(*new_options, name='name')


def upgrade():
    op.alter_column('role_permissions', 'name', type_=new_type)
    op.create_table('artist',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('code', sa.Unicode(length=255), nullable=True),
                    sa.Column('name', sa.Unicode(length=255), nullable=True),
                    sa.Column('kana', sa.Unicode(length=255), nullable=True),
                    sa.Column('url', sa.Unicode(length=255), nullable=True),
                    sa.Column('image', sa.Unicode(length=255), nullable=True),
                    sa.Column('description', MEDIUMTEXT(charset='utf8'), nullable=True),
                    sa.Column('public', sa.Boolean, nullable=False, default=True),
                    sa.Column('organization_id', sa.Integer(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    )

    op.execute("insert into role values(36, 'artist_viewer');")
    op.execute("insert into role values(37, 'artist_editor');")

    op.execute("insert into role_permissions values (273, 'artist_read', 1);")
    op.execute("insert into role_permissions values (274, 'artist_create', 1);")
    op.execute("insert into role_permissions values (275, 'artist_update', 1);")
    op.execute("insert into role_permissions values (276, 'artist_delete', 1);")
    op.execute("insert into role_permissions values (277, 'artist_read', 30);")
    op.execute("insert into role_permissions values (278, 'artist_create', 30);")
    op.execute("insert into role_permissions values (279, 'artist_update', 30);")
    op.execute("insert into role_permissions values (280, 'artist_delete', 30);")
    op.execute("insert into role_permissions values (281, 'artist_read', 36);")
    op.execute("insert into role_permissions values (282, 'artist_read', 37);")
    op.execute("insert into role_permissions values (283, 'artist_create', 37);")
    op.execute("insert into role_permissions values (284, 'artist_update', 37);")
    op.execute("insert into role_permissions values (285, 'artist_delete', 37);")


def downgrade():
    op.execute("delete from role_permissions where id = 273;")
    op.execute("delete from role_permissions where id = 274;")
    op.execute("delete from role_permissions where id = 275;")
    op.execute("delete from role_permissions where id = 276;")
    op.execute("delete from role_permissions where id = 277;")
    op.execute("delete from role_permissions where id = 278;")
    op.execute("delete from role_permissions where id = 279;")
    op.execute("delete from role_permissions where id = 280;")
    op.execute("delete from role_permissions where id = 281;")
    op.execute("delete from role_permissions where id = 282;")
    op.execute("delete from role_permissions where id = 283;")
    op.execute("delete from role_permissions where id = 284;")
    op.execute("delete from role_permissions where id = 285;")

    op.execute("delete from role where id = 36;")
    op.execute("delete from role where id = 37;")

    op.drop_table('artist')
    op.alter_column('role_permissions', 'name', type_=old_type)
