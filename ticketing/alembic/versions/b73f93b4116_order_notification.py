"""order_notification

Revision ID: b73f93b4116
Revises: 2e07bb5c93c9
Create Date: 2014-06-12 21:05:08.875414

"""

# revision identifiers, used by Alembic.
revision = 'b73f93b4116'
down_revision = '2e07bb5c93c9'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table(
        'OrderNotification',
        sa.Column('id', Identifier, primary_key=True),
        sa.Column('order_id', Identifier, nullable=False, unique=True),
        sa.Column('sej_remind_at', sa.DateTime(), nullable=True),
        )

def downgrade():
    op.drop_table('OrderNotification')
