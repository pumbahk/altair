"""create_checkin_token_reservation

Revision ID: 2b70bbe205d5
Revises: 1964706e096b
Create Date: 2014-03-14 10:07:00.120366

"""

# revision identifiers, used by Alembic.
revision = '2b70bbe205d5'
down_revision = '1964706e096b'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger
from sqlalchemy.dialects import mysql

def upgrade():
    op.create_table('CheckinTokenReservation',
    sa.Column('identity_id', Identifier(), nullable=False),
    sa.Column('token_id', Identifier(), nullable=False),
    sa.Column('expire_at', sa.DateTime(), nullable=False),
    sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
    sa.ForeignKeyConstraint(['identity_id'], ['CheckinIdentity.id'], ),
    sa.ForeignKeyConstraint(['token_id'], ['OrderedProductItemToken.id'], ),
    sa.PrimaryKeyConstraint('token_id', 'deleted_at'),
    sa.UniqueConstraint('token_id', 'deleted_at', name='ix_token_id_deleted_at'))

def downgrade():
    op.drop_table('CheckinTokenReservation')
