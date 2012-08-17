"""empty message

Revision ID: 40e909e8bf3c
Revises: 3584d649de05
Create Date: 2012-08-16 14:32:58.943984

"""

# revision identifiers, used by Alembic.
revision = '40e909e8bf3c'
down_revision = '10bf786de077'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf
from sqlalchemy.dialects import mysql
Identifier = sa.BigInteger

def upgrade():

    op.create_table('SejTenant',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('shop_name', sa.String(length=255), nullable=True),
        sa.Column('shop_id', sa.String(length=255), nullable=True),
        sa.Column('contact_01', sa.String(length=255), nullable=False),
        sa.Column('contact_02', sa.String(length=255), nullable=False),
        sa.Column('api_key', sa.String(length=255), nullable=True),
        sa.Column('inticket_api_url', sa.String(length=255), nullable=True),
        sa.Column('organization_id', Identifier(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('SejTenant')
