"""add_missing_columns_to_organization

Revision ID: 54385b1b2cdf
Revises: 493be3f09c7a
Create Date: 2014-01-21 10:07:27.697433

"""

# revision identifiers, used by Alembic.
revision = '54385b1b2cdf'
down_revision = '493be3f09c7a'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('Organization', sa.Column('company_name', sa.Unicode(255), nullable=True))
    op.add_column('Organization', sa.Column('section_name', sa.Unicode(255), nullable=True))
    op.add_column('Organization', sa.Column('zip', sa.Unicode(32), nullable=True))

def downgrade():
    op.drop_column('Organization', 'company_name')
    op.drop_column('Organization', 'section_name')
    op.drop_column('Organization', 'zip')
