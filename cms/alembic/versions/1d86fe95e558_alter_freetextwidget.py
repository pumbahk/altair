"""alter freetextwidget text

Revision ID: 1d86fe95e558
Revises: 126c50f99cd7
Create Date: 2012-06-07 10:15:37.715396

"""

# revision identifiers, used by Alembic.
revision = '1d86fe95e558'
down_revision = '126c50f99cd7'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column("widget_text", "text", type_=sa.Unicode(length=255), existing_type=sa.UnicodeText)

def downgrade():
    op.alter_column("widget_text", "text", existing_type=sa.Unicode(length=255), type_=sa.UnicodeText)

