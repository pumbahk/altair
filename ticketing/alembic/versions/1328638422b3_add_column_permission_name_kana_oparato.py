# -*- coding: utf-8 -*-
"""add column Permission.name_kana OparatorRole.name_kana

Revision ID: 1328638422b3
Revises: 3c93bddaec70
Create Date: 2014-02-28 19:07:25.272840

"""

# revision identifiers, used by Alembic.
revision = '1328638422b3'
down_revision = '3e2e37602d0b'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table('PermissionCategory',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('name', sa.Unicode(length=255), nullable=False),
        sa.Column('name_kana', sa.Unicode(length=255), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id')
        )
    op.execute(u"INSERT INTO PermissionCategory (id, name, name_kana) VALUES (1, 'administrator', 'オーガニゼーション管理')")
    op.execute(u"INSERT INTO PermissionCategory (id, name, name_kana) VALUES (2, 'event_viewer' , '公演管理閲覧')")
    op.execute(u"INSERT INTO PermissionCategory (id, name, name_kana) VALUES (3, 'event_editor' , '公演管理編集')")
    op.execute(u"INSERT INTO PermissionCategory (id, name, name_kana) VALUES (4, 'master_viewer', 'マスタ管理閲覧')")
    op.execute(u"INSERT INTO PermissionCategory (id, name, name_kana) VALUES (5, 'master_editor', 'マスタ管理編集')")
    op.execute(u"INSERT INTO PermissionCategory (id, name, name_kana) VALUES (6, 'sales_viewer' , '営業管理閲覧')")
    op.execute(u"INSERT INTO PermissionCategory (id, name, name_kana) VALUES (7, 'sales_editor' , '営業管理編集')")
    op.execute(u"INSERT INTO PermissionCategory (id, name, name_kana) VALUES (8, 'sales_counter', '窓口業務')")
    op.execute(u"INSERT INTO PermissionCategory (id, name, name_kana) VALUES (9, 'authenticated', '認証済みユーザー')")
    op.execute(u"INSERT INTO PermissionCategory (id, name, name_kana) VALUES (10,'everybody'    , '一般ユーザー')")
    op.execute(u"INSERT INTO PermissionCategory (id, name, name_kana) VALUES (11,'asset_viewer' , 'アセット閲覧')")
    op.execute(u"INSERT INTO PermissionCategory (id, name, name_kana) VALUES (12,'asset_editor' , 'アセット編集')")
    op.execute(u"INSERT INTO PermissionCategory (id, name, name_kana) VALUES (13,'magazine_viewer', 'マガジン閲覧')")
    op.execute(u"INSERT INTO PermissionCategory (id, name, name_kana) VALUES (14,'magazine_editor', 'マガジン編集')")
    op.execute(u"INSERT INTO PermissionCategory (id, name, name_kana) VALUES (15,'page_viewer'  , 'ページ閲覧')")
    op.execute(u"INSERT INTO PermissionCategory (id, name, name_kana) VALUES (16,'page_editor'  , 'ページ編集')")
    op.execute(u"INSERT INTO PermissionCategory (id, name, name_kana) VALUES (17,'topic_viewer' , 'トピック閲覧')")
    op.execute(u"INSERT INTO PermissionCategory (id, name, name_kana) VALUES (18,'ticket_editor', 'チケット編集')")
    op.execute(u"INSERT INTO PermissionCategory (id, name, name_kana) VALUES (19,'tag_editor'   , 'タグ編集')")
    op.execute(u"INSERT INTO PermissionCategory (id, name, name_kana) VALUES (20,'layout_viewer', 'レイアウト閲覧')")
    op.execute(u"INSERT INTO PermissionCategory (id, name, name_kana) VALUES (21,'layout_editor', 'レイアウト編集')")

    op.add_column('OperatorRole', sa.Column('name_kana', sa.Unicode(length=255), nullable=True))
    op.execute(u"UPDATE OperatorRole SET name_kana = 'Altair管理者' WHERE name = 'administrator'")
    op.execute(u"UPDATE OperatorRole SET name_kana = '管理者' WHERE name = 'superuser'")
    op.execute(u"UPDATE OperatorRole SET name_kana = 'オペレーター' WHERE name = 'operator'")
    op.execute(u"UPDATE OperatorRole SET name_kana = 'スーパーオペレーター' WHERE name = 'superoperator'")

    op.add_column(u'Permission', sa.Column('category_id', Identifier, nullable=True))
    op.create_foreign_key('Permission_ibfk_2', 'Permission', 'PermissionCategory', ['category_id'], ['id'])
    op.execute(u"UPDATE Permission p, PermissionCategory pc SET p.category_id = pc.id WHERE p.category_name = pc.name")
    op.drop_column(u'Permission', 'category_name')

def downgrade():
    op.add_column(u'Permission', sa.Column('category_name', sa.String(255)))
    op.execute(u"UPDATE Permission p, PermissionCategory pc SET p.category_name = pc.name WHERE p.category_id = pc.id")
    op.drop_constraint('Permission_ibfk_2', 'Permission', 'foreignkey')
    op.drop_column(u'Permission', 'category_id')

    op.drop_column('OperatorRole', 'name_kana')

    op.drop_table('PermissionCategory')
