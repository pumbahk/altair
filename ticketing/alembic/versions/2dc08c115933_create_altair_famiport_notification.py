"""create_altair_famiport_notification

Revision ID: 2dc08c115933
Revises: 51b5cda752e5
Create Date: 2015-07-14 16:56:00.043198

"""

# revision identifiers, used by Alembic.
revision = '2dc08c115933'
down_revision = '51b5cda752e5'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table(
        'AltairFamiPortNotification',
        sa.Column('id', Identifier, primary_key=True, autoincrement=True),
        sa.Column('type', sa.Integer, nullable=False),
        sa.Column('client_code', sa.Unicode(24), nullable=False),
        sa.Column('order_no', sa.Unicode(12), nullable=False),
        sa.Column('famiport_order_identifier', sa.Unicode(12), nullable=True),
        sa.Column('payment_reserve_number', sa.Unicode(13), nullable=True),
        sa.Column('ticketing_reserve_number', sa.Unicode(13), nullable=True),
        sa.Column('reflected_at', sa.DateTime(), nullable=True, index=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False)
        )

def downgrade():
    op.drop_table('AltairFamiPortNotification')
