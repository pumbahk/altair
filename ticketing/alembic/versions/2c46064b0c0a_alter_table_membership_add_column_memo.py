"""alter table Membership add column memo

Revision ID: 2c46064b0c0a
Revises: cba5b2d872c
Create Date: 2014-07-04 16:38:08.812527

"""

# revision identifiers, used by Alembic.
revision = '2c46064b0c0a'
down_revision = 'cba5b2d872c'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('Membership', sa.Column('memo', sa.Text(), nullable=True))

def downgrade():
    op.drop_column('Membership', 'memo')
