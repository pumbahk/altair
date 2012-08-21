"""empty message

Revision ID: 9ef25d188e3
Revises: 52fcb95562ea
Create Date: 2012-08-20 17:49:02.795411

"""

# revision identifiers, used by Alembic.
revision = '9ef25d188e3'
#down_revision = '52fcb95562ea'
down_revision = '19ead4ed557'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf
from sqlalchemy.dialects import mysql

Identifier = sa.BigInteger

def upgrade():
    op.create_table('TicketPrintQueue',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('operator_id', Identifier(), nullable=False),
        sa.Column('data', sa.String(length=65536), nullable=False, default=''),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['operator_id'], ['Operator.id'], 'ticketprintqueue_ibfk_1', ondelete='CASCADE'),
        )

def downgrade():
    op.drop_table('TicketPrintQueue')
