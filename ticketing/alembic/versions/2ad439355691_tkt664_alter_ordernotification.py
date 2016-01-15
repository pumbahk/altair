"""#tkt664 alter OrderNotification

Revision ID: 2ad439355691
Revises: 38b6b43b7e5d
Create Date: 2016-01-14 14:46:38.224330

"""

# revision identifiers, used by Alembic.
revision = '2ad439355691'
down_revision = '38b6b43b7e5d'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.alter_column('OrderNotification', 'sej_remind_at', new_column_name='payment_remind_at', existing_type=sa.DateTime(), nullable=True)

def downgrade():
    op.alter_column('OrderNotification', 'payment_remind_at', new_column_name='sej_remind_at', existing_type=sa.DateTime(), nullable=True)
