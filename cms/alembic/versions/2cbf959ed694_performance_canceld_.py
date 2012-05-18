"""performance canceld status

Revision ID: 2cbf959ed694
Revises: 3f193d0b24f4
Create Date: 2012-05-18 17:31:15.596293

"""

# revision identifiers, used by Alembic.
revision = '2cbf959ed694'
down_revision = '3f193d0b24f4'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column("performance", sa.Column("canceld", sa.Boolean))

def downgrade():
    op.drop_column("performance", "canceld")
