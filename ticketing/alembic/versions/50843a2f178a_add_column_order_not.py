"""add column Order.note

Revision ID: 50843a2f178a
Revises: a2b7618aece
Create Date: 2012-09-05 22:02:29.116702

"""

# revision identifiers, used by Alembic.
revision = '50843a2f178a'
down_revision = '586c92fc1931'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('Order', sa.Column('note', sa.UnicodeText(), nullable=True, default=None))

def downgrade():
    op.drop_column('Order', 'note')

