"""added_event_operator_and_sales_person_to_event

Revision ID: 5936c72c6490
Revises: 3a4d337b0d8d
Create Date: 2017-02-20 13:11:19.934481

"""

# revision identifiers, used by Alembic.
revision = '5936c72c6490'
down_revision = '3a4d337b0d8d'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('EventSetting', sa.Column('event_operator_id', Identifier(), nullable=True))
    op.add_column('EventSetting', sa.Column('sales_person_id', Identifier(), nullable=True))

def downgrade():
    op.drop_column('EventSetting', 'event_operator_id')
    op.drop_column('EventSetting', 'sales_person_id')
