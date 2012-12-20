"""add category.attributes

Revision ID: 2ad0f44f5142
Revises: 57feb087d5c7
Create Date: 2012-12-20 11:25:40.714270

"""

# revision identifiers, used by Alembic.
revision = '2ad0f44f5142'
down_revision = '57feb087d5c7'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('category', sa.Column('attributes', sa.Unicode(255), nullable=False, default=u""))

def downgrade():
    op.drop_column("category", "attributes")
