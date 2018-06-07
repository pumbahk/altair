"""rename receiption date columns of ResaleSegment

Revision ID: 34ed7cee0c78
Revises: 3f34af8d2a26
Create Date: 2018-06-05 17:05:37.458922

"""

# revision identifiers, used by Alembic.
revision = '34ed7cee0c78'
down_revision = '3f34af8d2a26'

from alembic import op
import sqlalchemy as sa

Identifier = sa.BigInteger


def upgrade():
    op.add_column('ResaleSegment', sa.Column('reception_start_at', sa.DateTime(), nullable=False))
    op.add_column('ResaleSegment', sa.Column('reception_end_at', sa.DateTime(), nullable=False))
    op.execute("UPDATE ResaleSegment SET reception_start_at=start_at, reception_end_at=end_at;")
    op.drop_column('ResaleSegment', 'start_at')
    op.drop_column('ResaleSegment', 'end_at')

def downgrade():
    op.add_column('ResaleSegment', sa.Column('start_at', sa.DateTime(), nullable=False))
    op.add_column('ResaleSegment', sa.Column('end_at', sa.DateTime(), nullable=False))
    op.execute("UPDATE ResaleSegment SET start_at=reception_start_at, end_at=reception_end_at;")
    op.drop_column('ResaleSegment', 'reception_start_at')
    op.drop_column('ResaleSegment', 'reception_end_at')
