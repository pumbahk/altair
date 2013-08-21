"""LotEntryReportSetting

Revision ID: 304ea58e981
Revises: 462e944c1c46
Create Date: 2013-07-26 14:17:27.125655

"""

# revision identifiers, used by Alembic.
revision = '304ea58e981'
down_revision = '1b8b46eff15'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger
from sqlalchemy.dialects import mysql

def upgrade():
    op.create_table('LotEntryReportSetting',
    sa.Column('id', Identifier(), nullable=False),
    sa.Column('event_id', Identifier(), nullable=True),
    sa.Column('lot_id', Identifier(), nullable=True),
    sa.Column('operator_id', Identifier(), nullable=True),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('frequency', sa.Integer(), nullable=False),
    sa.Column('period', sa.Integer(), nullable=False),
    sa.Column('time', sa.String(length=4), nullable=False),
    sa.Column('day_of_week', sa.Integer(), nullable=True),
    sa.Column('start_on', sa.DateTime(), nullable=True),
    sa.Column('end_on', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(), 
              server_default=text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), 
              nullable=False),
    sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
    sa.ForeignKeyConstraint(['event_id'], ['Event.id'], ),
    sa.ForeignKeyConstraint(['lot_id'], ['Lot.id'], ),
    sa.ForeignKeyConstraint(['operator_id'], ['Operator.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('LotEntryReportSetting')

