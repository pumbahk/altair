"""alter table OrderImportTask

Revision ID: 200f3c450446
Revises: 48a6f59b6834
Create Date: 2013-09-19 14:14:09.031283

"""

# revision identifiers, used by Alembic.
revision = '200f3c450446'
down_revision = '48a6f59b6834'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.drop_column('OrderImportTask', 'error')
    op.add_column('OrderImportTask', sa.Column('errors', sa.String(65536), nullable=True))

def downgrade():
    op.drop_column('OrderImportTask', 'errors')
    op.add_column('OrderImportTask', sa.Column('error', sa.UnicodeText(), nullable=True))
