"""category: add label

Revision ID: 48e82f3702e3
Revises: 137096ec0baa
Create Date: 2012-05-10 14:38:09.923649

"""

# revision identifiers, used by Alembic.
revision = '48e82f3702e3'
down_revision = '137096ec0baa'

from alembic import op
import sqlalchemy as sa
from altaircms.models import Category

def upgrade():
    op.add_column("category", 
                  sa.Column("label", sa.String(255)))
    op.add_column("category", 
                  sa.Column("imgsrc", sa.String(255)))
    op.add_column("category", 
                  sa.Column("orderno", sa.Integer))

def downgrade():
    op.drop_column("category", "label")
    op.drop_column("category", "imgsrc")
    op.drop_column("category", "orderno")

