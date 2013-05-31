"""alter table OrganizationSettings add column contact_pc_url and contact_mobile_url

Revision ID: 5129fbc59530
Revises: 186e089c4c62
Create Date: 2013-05-07 11:28:18.548505

"""

# revision identifiers, used by Alembic.
revision = '5129fbc59530'
down_revision = '186e089c4c62'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger
from sqlalchemy.dialects import mysql

def upgrade():
    op.add_column('OrganizationSetting', sa.Column('contact_pc_url', sa.Unicode(length=255), nullable=True))
    op.add_column('OrganizationSetting', sa.Column('contact_mobile_url', sa.Unicode(length=255), nullable=True))

def downgrade():
    op.drop_column('OrganizationSetting', 'contact_mobile_url')
    op.drop_column('OrganizationSetting', 'contact_pc_url')
