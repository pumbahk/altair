"""PageCover created

Revision ID: 4763d4675ab5
Revises: 2bb9f0027253
Create Date: 2013-08-12 13:56:30.688943

"""

# revision identifiers, used by Alembic.
revision = '4763d4675ab5'
down_revision = '2bb9f0027253'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger
from sqlalchemy.dialects import mysql

def upgrade():
    op.create_table('TicketCover',
                    sa.Column('id', Identifier(), nullable=False),
                    sa.Column('name', sa.Unicode(length=255), nullable=False),
                    sa.Column('operator_id', Identifier(), nullable=True),
                    sa.Column('organization_id', Identifier(), nullable=True),
                    sa.Column('ticket_id', Identifier(), nullable=False),
                    sa.Column('delivery_method_id', Identifier(), nullable=True),
                    sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
                    sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
                    sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
                    sa.ForeignKeyConstraint(['delivery_method_id'], ['DeliveryMethod.id'], ),
                    sa.ForeignKeyConstraint(['operator_id'], ['Operator.id'], ),
                    sa.ForeignKeyConstraint(['organization_id'], ['Organization.id'], ),
                    sa.ForeignKeyConstraint(['ticket_id'], ['Ticket.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )

def downgrade():
    op.drop_table('TicketCover')
