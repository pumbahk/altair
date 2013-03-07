"""OrganizationSetting

Revision ID: 40d78cfd6809
Revises: 27aa0c829578
Create Date: 2013-03-06 18:41:17.158908

"""

# revision identifiers, used by Alembic.
revision = '40d78cfd6809'
down_revision = '27aa0c829578'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger
from sqlalchemy.dialects import mysql

def upgrade():
    op.create_table('OrganizationSetting',
    sa.Column('id', Identifier(), nullable=False),
    sa.Column('name', sa.Unicode(length=255), nullable=True),
    sa.Column('organization_id', Identifier(), nullable=True),
    sa.Column('auth_type', sa.Unicode(length=255), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
    sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
    sa.ForeignKeyConstraint(['organization_id'], ['Organization.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('OrganizationSetting')
