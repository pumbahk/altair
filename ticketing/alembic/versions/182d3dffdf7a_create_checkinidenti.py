"""create CheckinIdentity for checkinstation

Revision ID: 182d3dffdf7a
Revises: 31e43f2db41b
Create Date: 2013-12-28 00:26:58.421242

"""

# revision identifiers, used by Alembic.
revision = '182d3dffdf7a'
down_revision = '31e43f2db41b'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger
from sqlalchemy.dialects import mysql

def upgrade():
    op.create_table('CheckinIdentity',
    sa.Column('id', Identifier(), nullable=False),
    sa.Column('operator_id', Identifier(), nullable=False),
    sa.Column('device_id', sa.String(length=64), nullable=False),
    sa.Column('login_at', sa.TIMESTAMP(), server_default=text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('logout_at', sa.TIMESTAMP(), nullable=True),
    sa.Column('secret', sa.String(length=32), nullable=False),
    sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
    sa.ForeignKeyConstraint(['operator_id'], ['Operator.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('CheckinIdentity')
