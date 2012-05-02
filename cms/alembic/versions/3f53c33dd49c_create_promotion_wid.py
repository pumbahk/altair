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
    op.create_table("promotion", 
                    sa.Column("id", sa.Integer(), nullable=False), 
                    sa.Column("name", sa.Unicode(length=255), index=True), 
                    sa.Column("site_id", sa.Integer), 
                    sa.ForeignKeyConstraint(["site_id"], ["site.id"]), 
                    sa.PrimaryKeyConstraint("id")
                    )
    op.create_table("promotion_unit", 
                    sa.Column("id", sa.Integer(), nullable=False), 
                    sa.Column("promotion_id", sa.Integer(), nullable=False), 
                    sa.Column("main_image_id", sa.Integer()), 
                    sa.Column("thumbnail_id", sa.Integer()), 
                    sa.Column("pageset_id", sa.Integer()), 
                    sa.Column("link", sa.Unicode(length=255)), 
                    sa.Column("text", sa.UnicodeText), 
                    sa.ForeignKeyConstraint(["main_image_id"], ["image_asset.id"]), 
                    sa.ForeignKeyConstraint(["thumbnail_id"], ["image_asset.id"]), 
                    sa.ForeignKeyConstraint(["promotion_id"], ["promotion.id"]), 
                    sa.PrimaryKeyConstraint("id"), 
                    sa.ForeignKeyConstraint(["pageset_id"], ["pagesets.id"]), 
                    )
    op.create_table('widget_promotion',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('items', sa.Unicode(length=255), nullable=True),
                    sa.Column("promotion_id", sa.Integer(), nullable=False), 
                    sa.ForeignKeyConstraint(['id'], ['widget.id'], ),
                    sa.ForeignKeyConstraint(['promotion_id'], ['promotion.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )

def downgrade():
    op.drop_table("widget_promotion")
    op.drop_table("promotion_unit")
    op.drop_table("promotion")

