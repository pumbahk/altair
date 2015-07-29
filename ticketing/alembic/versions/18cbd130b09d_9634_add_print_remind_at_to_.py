"""#9634 add print_remind_at to OrderNotification

Revision ID: 18cbd130b09d
Revises: 5679f66a3ff8
Create Date: 2015-07-15 11:59:34.341330

"""

# revision identifiers, used by Alembic.
revision = '18cbd130b09d'
down_revision = '5679f66a3ff8'

from alembic import op
import sqlalchemy as sa

Identifier = sa.BigInteger


def upgrade():
    op.add_column('OrderNotification', sa.Column('print_remind_at', sa.DateTime(), nullable=True))

def downgrade():
    op.drop_column('OrderNotification', 'print_remind_at')
