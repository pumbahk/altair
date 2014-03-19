"""alter table widget_ticketlist add column show_seattype

Revision ID: d49d1b04a0c
Revises: 24f52aaf309f
Create Date: 2014-03-19 11:32:08.455343

"""

# revision identifiers, used by Alembic.
revision = 'd49d1b04a0c'
down_revision = '24f52aaf309f'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text

def upgrade():
    op.add_column('widget_ticketlist', sa.Column('show_seattype', sa.Boolean(), nullable=False,default=True, server_default=text('1')))
def downgrade():
    op.drop_column('widget_ticketlist', 'show_seattype')
