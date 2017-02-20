"""added_event_creator_and_operator_to_event

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
    op.add_column('Event', sa.Column('event_creator', sa.Unicode(length=255), nullable=True))
    op.add_column('Event', sa.Column('event_operator', sa.Unicode(length=255), nullable=True))

def downgrade():
    op.drop_column('Event', 'event_creator')
    op.drop_column('Event', 'event_operator')
