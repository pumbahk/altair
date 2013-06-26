"""LotWorkHistory

Revision ID: 134458f9ae23
Revises: 23d59b1d8131
Create Date: 2013-06-25 17:22:17.298305

"""

# revision identifiers, used by Alembic.
revision = '134458f9ae23'
down_revision = 'b6c72d434f9'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('LotWorkHistory',
    sa.Column('id', sa.Identifier(), nullable=False),
    sa.Column('lot_id', sa.Identifier(), nullable=True),
    sa.Column('entry_no', sa.Unicode(length=20), nullable=False),
    sa.Column('wish_order', sa.Integer(), nullable=True),
    sa.Column('error', sa.UnicodeText(), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(), server_default='CURRENT_TIMESTAMP', nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default='0', nullable=False),
    sa.ForeignKeyConstraint(['lot_id'], ['Lot.id'], ),
    sa.PrimaryKeyConstraint('id'),
    )
    ### end Alembic commands ###

def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('LotWorkHistory')
    ### end Alembic commands ###
