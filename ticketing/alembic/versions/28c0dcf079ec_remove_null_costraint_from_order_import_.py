"""remove_null_costraint_from_order_import_task

Revision ID: 28c0dcf079ec
Revises: 278bf2f5a4bd
Create Date: 2014-04-24 23:45:46.814192

"""

# revision identifiers, used by Alembic.
revision = '28c0dcf079ec'
down_revision = '278bf2f5a4bd'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.alter_column(u'OrderImportTask', 'performance_id', existing_type=Identifier, nullable=True)
    op.alter_column(u'OrderImportTask', 'data', existing_type=sa.UnicodeText(8388608), nullable=True)

def downgrade():
    op.alter_column(u'OrderImportTask', 'performance_id', existing_type=Identifier, nullable=False)
    op.alter_column(u'OrderImportTask', 'data', existing_type=sa.UnicodeText(8388608), nullable=False)
