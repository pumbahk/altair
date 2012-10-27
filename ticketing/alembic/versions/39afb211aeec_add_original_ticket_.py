"""add_original_ticket_id_to_ticket

Revision ID: 39afb211aeec
Revises: 5449082bc305
Create Date: 2012-10-27 08:46:34.377887

"""

# revision identifiers, used by Alembic.
revision = '39afb211aeec'
down_revision = '5449082bc305'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('Ticket', sa.Column('original_ticket_id', Identifier, nullable=True))
    op.create_foreign_key('Ticket_ibfk_4', 'Ticket', 'Ticket', ['original_ticket_id'], ['id'], ondelete='SET NULL')

def downgrade():
    op.drop_constraint('Ticket_ibfk_4', 'Ticket', 'foreignkey')
    op.drop_column('Ticket', 'original_ticket_id')
