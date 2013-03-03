"""alter table SejRefundTicket add column sent_at

Revision ID: 3ee99f3f1e61
Revises: 5311fff7b14a
Create Date: 2013-02-25 10:26:30.619231

"""

# revision identifiers, used by Alembic.
revision = '3ee99f3f1e61'
down_revision = '5311fff7b14a'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('SejRefundTicket', sa.Column('sent_at', sa.DateTime(), nullable=True))
    op.alter_column('SejTicketTemplateFile', 'send_at', name='sent_at', type_=sa.DateTime, existing_type=sa.DateTime)

def downgrade():
    op.drop_column('SejRefundTicket', 'sent_at')
    op.alter_column('SejTicketTemplateFile', 'sent_at', name='send_at', type_=sa.DateTime, existing_type=sa.DateTime)
