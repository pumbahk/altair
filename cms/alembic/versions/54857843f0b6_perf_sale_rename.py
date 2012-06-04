"""performance_sale_rename_close_on_to_end_on

Revision ID: 54857843f0b6
Revises: 2cbf959ed694
Create Date: 2012-05-24 22:53:05.559769

"""

# revision identifiers, used by Alembic.
revision = '54857843f0b6'
down_revision = '2cbf959ed694'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column("performance", "close_on", existing_type=sa.DateTime, name="end_on")
    op.alter_column("sale", "close_on", existing_type=sa.DateTime, name="end_on")

def downgrade():
    op.alter_column("performance", "end_on", existing_type=sa.DateTime, name="close_on")
    op.alter_column("sale", "end_on", existing_type=sa.DateTime, name="close_on")
