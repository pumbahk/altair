"""alter table Order drop column cancel_reason

Revision ID: 209a1863fc22
Revises: 5278077a5232
Create Date: 2013-02-18 14:44:28.098154

"""

# revision identifiers, used by Alembic.
revision = '209a1863fc22'
down_revision = '5278077a5232'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.drop_column('Order', 'cancel_reason')

def downgrade():
    op.add_column('Order', sa.Column('cancel_reason', sa.String(length=32), nullable=True, default=None))
