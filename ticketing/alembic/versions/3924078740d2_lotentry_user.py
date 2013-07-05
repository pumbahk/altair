"""LotEntry.user

Revision ID: 3924078740d2
Revises: 4838962beb11
Create Date: 2013-06-20 18:03:00.986968

"""

# revision identifiers, used by Alembic.
revision = '3924078740d2'
down_revision = '4838962beb11'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('LotEntry',
                  sa.Column('user_id', Identifier, sa.ForeignKey('User.id', name='LotEntry_ibfk_7')))

def downgrade():
    op.drop_constraint('LotEntry_ibfk_7', 'LotEntry', type='foreignkey')
    op.drop_column('LotEntry', 'user_id')
