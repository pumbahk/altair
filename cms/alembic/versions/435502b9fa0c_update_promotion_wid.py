""" update promotion model

Revision ID: 435502b9fa0c
Revises: 1b83e811f262
Create Date: 2012-07-10 16:15:20.557974

"""

# revision identifiers, used by Alembic.
revision = '435502b9fa0c'
down_revision = '1b83e811f262'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    op.create_table('kind',
    sa.Column('organization_id', sa.Integer(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.Unicode(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('promotion2kind',
    sa.Column('promotion_id', sa.Integer(), nullable=True),
    sa.Column('kind_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['kind_id'], ['kind.id'], ),
    sa.ForeignKeyConstraint(['promotion_id'], ['promotion.id'], ),
    sa.PrimaryKeyConstraint()
    )
    op.drop_table(u'promotion_unit')
    op.drop_column(u'event', u'client_id')
    op.alter_column(u'organization', u'auth_source', 
               existing_type=mysql.VARCHAR(length=255), 
               nullable=True)
    op.drop_column(u'performance', u'client_id')
    op.add_column(u'promotion', sa.Column('main_image_id', sa.Integer(), nullable=True))
    op.add_column(u'promotion', sa.Column('thumbnail_id', sa.Integer(), nullable=True))
    op.add_column(u'promotion', sa.Column('text', sa.UnicodeText(), nullable=True))
    op.add_column(u'promotion', sa.Column('link', sa.Unicode(length=255), nullable=True))
    op.add_column(u'promotion', sa.Column('linked_page_id', sa.Integer(), nullable=True))
    op.drop_column(u'promotion', u'name')

    op.add_column('promotion', sa.Column('publish_close_on', sa.DateTime(), nullable=True))
    op.add_column('promotion', sa.Column('orderno', sa.Integer(), nullable=True))
    op.add_column('promotion', sa.Column('publish_open_on', sa.DateTime(), nullable=True))
    op.add_column('promotion', sa.Column('is_vetoed', sa.Boolean(), nullable=True))
    op.add_column('widget_promotion', sa.Column('kind_id', sa.Integer(), nullable=True))
    op.add_column('widget_promotion', sa.Column('display_type', sa.Unicode(length=255), nullable=True))
    op.execute("ALTER TABLE widget_promotion DROP FOREIGN KEY fk_widget_promotion_promotion_id_to_promotion_id;")
    op.drop_column('widget_promotion', u'promotion_id')
    op.drop_column('widget_promotion', u'kind')

def downgrade():
    op.add_column('widget_promotion', sa.Column(u'kind', mysql.VARCHAR(length=255), nullable=True))
    op.add_column('widget_promotion', sa.Column(u'promotion_id', mysql.INTEGER(display_width=11), nullable=True))
    op.drop_column('widget_promotion', 'display_type')
    op.drop_column('widget_promotion', 'kind_id')
    op.add_column('promotion', sa.Column(u'target', mysql.VARCHAR(length=255), nullable=True))
    op.drop_column('promotion', 'is_vetoed')
    op.drop_column('promotion', 'publish_open_on')
    op.drop_column('promotion', 'orderno')
    op.drop_column('promotion', 'publish_close_on')
    op.add_column(u'promotion', sa.Column(u'name', mysql.VARCHAR(length=255), nullable=True))
    op.drop_column(u'promotion', 'linked_page_id')
    op.drop_column(u'promotion', 'link')
    op.drop_column(u'promotion', 'text')
    op.drop_column(u'promotion', 'thumbnail_id')
    op.drop_column(u'promotion', 'main_image_id')
    op.add_column(u'performance', sa.Column(u'client_id', mysql.INTEGER(display_width=11), nullable=True))
    op.alter_column(u'organization', u'auth_source', 
               existing_type=mysql.VARCHAR(length=255), 
               nullable=False)
    op.add_column(u'event', sa.Column(u'client_id', mysql.INTEGER(display_width=11), nullable=True))
    op.create_table(u'promotion_unit',
    sa.Column(u'id', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column(u'promotion_id', mysql.INTEGER(display_width=11), nullable=True),
    sa.Column(u'main_image_id', mysql.INTEGER(display_width=11), nullable=True),
    sa.Column(u'thumbnail_id', mysql.INTEGER(display_width=11), nullable=True),
    sa.Column(u'text', mysql.TEXT(), nullable=True),
    sa.Column(u'link', mysql.VARCHAR(length=255), nullable=True),
    sa.Column(u'pageset_id', mysql.INTEGER(display_width=11), nullable=True),
    sa.Column(u'organization_id', mysql.INTEGER(display_width=11), nullable=True),
    sa.ForeignKeyConstraint(['main_image_id'], [u'image_asset.id'], name=u'fk_promotion_unit_main_image_id_to_image_asset_id'),
    sa.ForeignKeyConstraint(['pageset_id'], [u'pagesets.id'], name=u'fk_promotion_unit_pageset_id_to_pagesets_id'),
    sa.ForeignKeyConstraint(['promotion_id'], [u'promotion.id'], name=u'fk_promotion_unit_promotion_id_promotion_id'),
    sa.ForeignKeyConstraint(['thumbnail_id'], [u'image_asset.id'], name=u'fk_promotion_unit_thumbnail_id_to_image_asset_id'),
    sa.PrimaryKeyConstraint(u'id')
    )
    op.drop_table('promotion2kind')
    op.drop_table('kind')
    op.drop_column('promotion', 'is_vetoed')
    op.drop_column('promotion', 'publish_open_on')
    op.drop_column('promotion', 'orderno')
    op.drop_column('promotion', 'publish_close_on')
