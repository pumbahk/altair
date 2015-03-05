"""add_merge_order_attributes_to_order_import_task

Revision ID: 492ca8fdfa1e
Revises: 287cb4bede2b
Create Date: 2015-03-05 13:54:48.273825

"""

# revision identifiers, used by Alembic.
revision = '492ca8fdfa1e'
down_revision = '287cb4bede2b'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('OrderImportTask', sa.Column('merge_order_attributes', sa.Boolean(), default=False, nullable=False))

def downgrade():
    op.drop_column('OrderImportTask', 'merge_order_attributes')
