"""add asset operator field(created_by, updated_by)

Revision ID: 2e08e4e22fe6
Revises: 53efa70a2dca
Create Date: 2012-04-18 13:38:53.093414

"""

# revision identifiers, used by Alembic.
revision = '2e08e4e22fe6'
down_revision = '53efa70a2dca'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column("asset", 
                  sa.Column("title", sa.Unicode(255)))
    op.add_column("asset", 
                  sa.Column("created_by_id", sa.INTEGER, sa.ForeignKey("operator.id")))
    op.add_column("asset", 
                  sa.Column("updated_by_id", sa.INTEGER, sa.ForeignKey("operator.id")))

def downgrade():
    op.drop_column("asset", "title")
    op.drop_column("asset", "created_by_id")
    op.drop_column("asset", "updated_by_id")

    
