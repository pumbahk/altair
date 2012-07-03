"""widget structure as text

Revision ID: 170847cf5bb5
Revises: 42e1fa2bca08
Create Date: 2012-06-11 20:11:25.784081

"""

# revision identifiers, used by Alembic.
revision = '170847cf5bb5'
down_revision = '42e1fa2bca08'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column("widgetdisposition", "structure", type_=sa.Text, existing_type=sa.String(length=255))

def downgrade():
    op.alter_column("widgetdisposition", "structure", existing_type=sa.Text, type_=sa.String(length=255))

