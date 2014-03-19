"""change_gettii_seat_seat_id

Revision ID: 4a89e94a84d9
Revises: 22cc5e6f1f20
Create Date: 2014-03-19 13:45:49.664356

"""

# revision identifiers, used by Alembic.
revision = '4a89e94a84d9'
down_revision = '22cc5e6f1f20'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.alter_column('GettiiSeat', 'seat_id', nullable=True,
                    new_column_name='seat_id', existing_type=Identifier, existing_nullable=False)

def downgrade():
    op.alter_column('GettiiSeat', 'seat_id', nullable=False,
                    new_column_name='seat_id', existing_type=Identifier, existing_nullable=True)
