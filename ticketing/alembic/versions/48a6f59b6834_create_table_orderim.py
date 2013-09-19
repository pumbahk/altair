"""create table OrderImportTask

Revision ID: 48a6f59b6834
Revises: 378db2b9f0bd
Create Date: 2013-09-18 13:40:42.571256

"""

# revision identifiers, used by Alembic.
revision = '48a6f59b6834'
down_revision = '230e47abb060'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table('OrderImportTask',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('organization_id', Identifier(), nullable=False),
        sa.Column('performance_id', Identifier(), nullable=False),
        sa.Column('operator_id', Identifier(), nullable=False),
        sa.Column('import_type', sa.Integer(), nullable=False),
        sa.Column('status', sa.Integer(), nullable=False),
        sa.Column('count', sa.Integer(), nullable=False),
        sa.Column('data', sa.UnicodeText(length=8388608), nullable=False),
        sa.Column('error', sa.UnicodeText(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['organization_id'], ['Organization.id'], 'OrderImportTask_ibfk_1', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['performance_id'], ['Performance.id'], 'OrderImportTask_ibfk_2', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['operator_id'], ['Operator.id'], 'OrderImportTask_ibfk_3', ondelete='CASCADE')
        )

def downgrade():
    op.drop_table('OrderImportTask')

