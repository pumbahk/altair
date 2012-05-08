"""create promotion widget

Revision ID: 3f53c33dd49c
Revises: c770ad39dd1
Create Date: 2012-05-02 10:39:41.847081

"""

# revision identifiers, used by Alembic.
revision = '3f53c33dd49c'
down_revision = 'c770ad39dd1'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(u'promotion',
    sa.Column(u'id', sa.Integer(), nullable=False),
    sa.Column(u'name', sa.Unicode(length=255), nullable=False),
    sa.Column(u'site_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['site_id'], [u'site.id'], name=u'fk_site_id'),
    sa.PrimaryKeyConstraint(u'id')
    )
    op.create_table(u"promotion_unit", 
                    sa.Column("id", sa.Integer(), nullable=False), 
                    sa.Column("promotion_id", sa.Integer(), nullable=False), 
                    sa.Column("main_image_id", sa.Integer()), 
                    sa.Column("thumbnail_id", sa.Integer()), 
                    sa.Column("pageset_id", sa.Integer()), 
                    sa.Column("link", sa.Unicode(length=255)), 
                    sa.Column("text", sa.UnicodeText), 
                    sa.ForeignKeyConstraint(["main_image_id"], ["image_asset.id"], name="fk_main_image_id"), 
                    sa.ForeignKeyConstraint(["thumbnail_id"], ["image_asset.id"], name="fk_thumbnail_id"), 
                    sa.ForeignKeyConstraint(["promotion_id"], ["promotion.id"], name="fk_promotion_unit_promotion_id"), 
                    sa.PrimaryKeyConstraint("id"), 
                    sa.ForeignKeyConstraint(["pageset_id"], ["pagesets.id"], name="fk_pageset_id"), 
                    )
    op.create_table(u'widget_promotion',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('items', sa.Unicode(length=255), nullable=True),
                    sa.Column("promotion_id", sa.Integer(), nullable=False), 
                    sa.ForeignKeyConstraint(['id'], ['widget.id'], name="fk_id_widget_id"),
                    sa.ForeignKeyConstraint(['promotion_id'], ['promotion.id'], name="fk_widget_promotion_id"),
                    sa.PrimaryKeyConstraint('id')
                    )

def downgrade():
    op.execute("ALTER TABLE widget_promotion DROP FOREIGN KEY fk_id_widget_id")
    op.execute("ALTER TABLE widget_promotion DROP FOREIGN KEY fk_widget_promotion_id")
    op.drop_table("widget_promotion")

    op.execute("ALTER TABLE promotion_unit DROP FOREIGN KEY fk_promotion_unit_promotion_id")
    op.execute("ALTER TABLE promotion_unit DROP FOREIGN KEY fk_main_image_id")
    op.execute("ALTER TABLE promotion_unit DROP FOREIGN KEY fk_thumbnail_id")
    op.execute("ALTER TABLE promotion_unit DROP FOREIGN KEY fk_pageset_id")
    op.drop_table("promotion_unit")

    op.execute("ALTER TABLE promotion DROP FOREIGN KEY fk_site_id")
    op.drop_table("promotion")

