"""create_table_notify_update_ticket_info_task

Revision ID: 3f8810964ed2
Revises: 3ca4e33768b4
Create Date: 2018-09-28 15:24:51.732847

"""

# revision identifiers, used by Alembic.
revision = '3f8810964ed2'
down_revision = '3ca4e33768b4'

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table('NotifyUpdateTicketInfoTask',
                    sa.Column('id', Identifier(), nullable=False),
                    sa.Column('ticket_bundle_id', Identifier(), nullable=False),
                    sa.Column('operator_id', Identifier(), nullable=False),
                    sa.Column('status', sa.Integer(), nullable=False),
                    sa.Column('errors', sa.Text, nullable=True),
                    sa.Column('created_at', sa.TIMESTAMP(), server_default=text('CURRENT_TIMESTAMP'), nullable=False),
                    sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
                    sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
                    sa.ForeignKeyConstraint(
                        ['ticket_bundle_id'],
                        ['TicketBundle.id'],
                        'NotifyUpdateTicketInfoTask_ibfk_1'
                    ),
                    sa.ForeignKeyConstraint(
                        ['operator_id'],
                        ['Operator.id'],
                        'NotifyUpdateTicketInfoTask_ibfk_2',
                    ),
                    sa.PrimaryKeyConstraint('id')
                    )


def downgrade():
    op.drop_table('NotifyUpdateTicketInfoTask')
