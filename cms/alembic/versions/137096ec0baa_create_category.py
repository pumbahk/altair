"""create category

Revision ID: 137096ec0baa
Revises: 55bca57cdb27
Create Date: 2012-05-08 18:13:43.763636

"""

# revision identifiers, used by Alembic.
revision = '137096ec0baa'
down_revision = '55bca57cdb27'

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(u"category", 
                    sa.Column(u"id",sa.Integer, primary_key=True, nullable=False), 
                    sa.Column(u"site_id", sa.Integer, sa.ForeignKey("site.id")),
                    sa.Column(u"parent_id", sa.Integer, sa.ForeignKey("category.id")),
                    sa.Column(u"name", sa.Unicode(length=255), nullable=False),
                    sa.Column(u"hierarchy", sa.Unicode(length=255), nullable=False),
                    sa.Column(u"url", sa.Unicode(length=255)),
                    sa.Column(u"pageset_id", sa.Integer, sa.ForeignKey("pagesets.id")), 
                    sa.UniqueConstraint("site_id", "name")
                    )


def downgrade():
    op.drop_table("category")
