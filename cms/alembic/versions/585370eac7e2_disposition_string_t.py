"""disposition:string->text

Revision ID: 585370eac7e2
Revises: 3547c611528b
Create Date: 2012-05-31 16:48:13.762528

"""

# revision identifiers, used by Alembic.
revision = '585370eac7e2'
down_revision = '3547c611528b'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column("widgetdisposition", "blocks", type_=sa.Text, existing_type=sa.String(255))
    op.alter_column("widgetdisposition", "structure", type_=sa.Text, existing_type=sa.String(255))

def downgrade():
    op.alter_column("widgetdisposition", "blocks", existing_type=sa.Text, type_=sa.String(255))
    op.alter_column("widgetdisposition", "structure", existing_type=sa.Text, type_=sa.String(255))
