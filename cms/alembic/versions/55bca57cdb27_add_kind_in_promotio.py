"""add kind in promotion widget

Revision ID: 55bca57cdb27
Revises: a8ad1c29da9
Create Date: 2012-05-07 21:47:55.318785

"""

# revision identifiers, used by Alembic.
revision = '55bca57cdb27'
down_revision = 'a8ad1c29da9'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column("widget_promotion", sa.Column("kind", sa.Unicode(255), nullable=False))


def downgrade():
    op.drop_column("widget_promotion", "kind")
