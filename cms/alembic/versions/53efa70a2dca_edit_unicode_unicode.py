"""edit unicode -> UnicodeText

Revision ID: 53efa70a2dca
Revises: 5383f63a769e
Create Date: 2012-04-17 18:20:59.035930

"""

# revision identifiers, used by Alembic.
revision = '53efa70a2dca'
down_revision = '5383f63a769e'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column("page",  "structure",  type_=sa.Text, existing_type=sa.String(length=255))
    op.alter_column("layout",  "blocks",   type_=sa.Text, existing_type=sa.String(length=255))

    op.alter_column("widget_menu",  "items",  type_=sa.UnicodeText, existing_type=sa.String(length=255))
    op.alter_column("widget_summary",  "items",  type_=sa.UnicodeText, existing_type=sa.String(length=255))

def downgrade():
    op.alter_column("page",  "structure",  type_=sa.String(length=255), existing_type=sa.Text)
    op.alter_column("layout",  "blocks",  type_=sa.String(length=255), existing_type=sa.Text)
    op.alter_column("widget_menu",  "items",  type_=sa.String(length=255),  existing_type=sa.UnicodeText)
    op.alter_column("widget_summary",  "items", type_=sa.String(length=255), existing_type=sa.UnicodeText )
