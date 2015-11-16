"""add_emergency_exit_url_to_organization

Revision ID: 277863733337
Revises: 3e665c8528c8
Create Date: 2015-11-16 14:36:14.435735

"""

# revision identifiers, used by Alembic.
revision = '277863733337'
down_revision = '3e665c8528c8'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('Organization', sa.Column('emergency_exit_url', sa.Unicode(255), nullable=True, default=None))

def downgrade():
    op.drop_column('Organization', 'emergency_exit_url')
