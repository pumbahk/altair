"""add_userside_token_id_column_to_FamiPortTicket

Revision ID: d068c02f6e6
Revises: 348dda4616af
Create Date: 2016-04-15 18:19:36.030551

"""

# revision identifiers, used by Alembic.
revision = 'd068c02f6e6'
down_revision = '348dda4616af'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('FamiPortTicket', sa.Column('userside_token_id', Identifier(), nullable=True))

def downgrade():
    op.drop_column(u'FamiPortTicket', 'userside_token_id')
