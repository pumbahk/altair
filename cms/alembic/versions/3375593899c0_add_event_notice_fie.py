"""add event.notice field

Revision ID: 3375593899c0
Revises: 560ea70c16f0
Create Date: 2012-06-18 09:34:30.624969

"""

# revision identifiers, used by Alembic.
revision = '3375593899c0'
down_revision = '560ea70c16f0'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column("event", sa.Column("notice", sa.UnicodeText))
    op.add_column("event", sa.Column("performers", sa.UnicodeText))


def downgrade():
    op.drop_column("event", "notice")
    op.drop_column("event", "performers")

