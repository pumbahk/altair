# revision identifiers, used by Alembic.
revision = '40001eedf727'
down_revision = 'a4caeb81d1b'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    op.add_column('Ticket', sa.Column('filename', sa.Unicode(length=255), nullable=False))
    op.execute("update Ticket set filename = \"-\";")


def downgrade():
    op.drop_column('Ticket', 'filename')

