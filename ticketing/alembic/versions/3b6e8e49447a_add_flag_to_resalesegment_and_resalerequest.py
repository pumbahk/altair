"""add flag to ResaleSegment and ResaleRequest

Revision ID: 3b6e8e49447a
Revises: 3bb7c88556eb
Create Date: 2018-04-06 11:23:29.340441

"""

# revision identifiers, used by Alembic.
revision = '3b6e8e49447a'
down_revision = '3bb7c88556eb'

from alembic import op
import sqlalchemy as sa

Identifier = sa.BigInteger


def upgrade():
    # ResaleSegment
    op.add_column('ResaleSegment', sa.Column('sent_status', sa.Integer(), default=1, server_default='1', index=True))
    # ResaleRequest
    op.add_column('ResaleRequest', sa.Column('sent_at', sa.TIMESTAMP, nullable=True))
    op.add_column('ResaleRequest', sa.Column('sent_status', sa.Integer(), default=1, server_default='1', index=True))
    op.add_column('ResaleRequest', sa.Column('status', sa.Integer(), default=1, server_default='1', index=True))
    op.drop_column('ResaleRequest', 'sold')

def downgrade():
    # ResaleRequest
    op.add_column('ResaleRequest', sa.Column('sold', sa.Boolean(), nullable=False, default=False, server_default='0', index=True))
    op.drop_column('ResaleRequest', 'sent_at')
    op.drop_column('ResaleRequest', 'sent_status')
    op.drop_column('ResaleRequest', 'status')
    # ResaleSegment
    op.drop_column('ResaleSegment', 'sent_status')
