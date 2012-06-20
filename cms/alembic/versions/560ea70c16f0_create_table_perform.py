"""create table performance_ticket_table

Revision ID: 560ea70c16f0
Revises: 5845518c2329
Create Date: 2012-06-19 12:08:35.576136

"""

# revision identifiers, used by Alembic.
revision = '560ea70c16f0'
down_revision = '5845518c2329'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('performance_ticket',
        sa.Column('performance_id', sa.Integer),
        sa.Column('ticket_id', sa.Integer),
        sa.ForeignKeyConstraint(['performance_id'], ['performance.id'], name="fk_performance_ticket_performance_id_to_performance_id"),
        sa.ForeignKeyConstraint(['ticket_id'], ['ticket.id'], name="fk_performance_ticket_ticket_id_to_ticket_id"),
        )

def downgrade():
    op.drop_table('performance_ticket')
