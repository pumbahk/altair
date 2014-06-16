"""add Ticket.base_template_id

Revision ID: e6d2bfcc31e
Revises: 379d8f5fb25
Create Date: 2014-05-30 02:53:54.410841

"""

# revision identifiers, used by Alembic.
revision = 'e6d2bfcc31e'
down_revision = '379d8f5fb25'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger
from sqlalchemy.dialects import mysql

def upgrade():
    op.add_column('Ticket', sa.Column('base_template_id', Identifier, nullable=True))
    op.create_foreign_key('Ticket_ibfk_5', 'Ticket', 'Ticket', ['base_template_id'], ['id'], ondelete='SET NULL')

def downgrade():
    op.drop_constraint('Ticket_ibfk_5', 'Ticket', 'foreignkey')
    op.drop_column('Ticket', 'base_template_id')
