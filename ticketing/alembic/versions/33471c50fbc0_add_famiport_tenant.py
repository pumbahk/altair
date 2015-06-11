# -*- coding: utf-8 -*-
"""add_amiport_tenant

Revision ID: 33471c50fbc0
Revises: c35141f8f11
Create Date: 2015-04-22 15:03:39.513828

"""

# revision identifiers, used by Alembic.
revision = '33471c50fbc0'
down_revision = 'c35141f8f11'


from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf
from datetime import date, time

Identifier = sa.BigInteger


def upgrade():
    op.create_table(
        'FamiPortTenant',
        sa.Column('id', Identifier, autoincrement=True, primary_key=True),
        sa.Column('organization_id', Identifier, sa.ForeignKey('Organization.id')),
        sa.Column('name', sa.Unicode(255), nullable=False),
        sa.Column('code', sa.Unicode(24), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.UniqueConstraint('organization_id', 'code')
        )

def downgrade():
    op.drop_table('FamiPortTenant')
