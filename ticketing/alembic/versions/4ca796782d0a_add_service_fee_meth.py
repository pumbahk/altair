"""add_service_fee_methods

Revision ID: 4ca796782d0a
Revises: 18849a570d67
Create Date: 2013-09-10 11:13:40.179891

"""

# revision identifiers, used by Alembic.
revision = '4ca796782d0a'
down_revision = '230e47abb060'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger

def upgrade():
    op.create_table('ServiceFeeMethod',
                    sa.Column('id', Identifier(), nullable=False),
                    sa.Column('name', sa.String(length=255), nullable=True), 
                    sa.Column('description', sa.String(length=1024), nullable=True),                   
                    sa.Column('fee', sa.Numeric(precision=16, scale=2), nullable=False, default=0),
                    sa.Column('fee_type', sa.Integer(), nullable=False, default=0),
                    sa.Column('organization_id', Identifier(), nullable=True),
                    sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
                    sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
                    sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
                    sa.Column('system_fee_default', sa.Boolean(), nullable=True),
                    sa.ForeignKeyConstraint(['organization_id'], ['Organization.id'], 'ServiceFeeMethod_ibfk_1'),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.add_column('PaymentDeliveryMethodPair', sa.Column('system_fee_type', sa.Integer(), nullable=False, default=0))

def downgrade():
    op.drop_table('ServiceFeeMethod')
    op.drop_column('PaymentDeliveryMethodPair', 'system_fee_type')

