"""alter table widget_text change text column

Revision ID: c09a614defd
Revises: 500167ad61bd
Create Date: 2015-01-29 17:51:01.173027

"""

# revision identifiers, used by Alembic.
revision = 'c09a614defd'
down_revision = '500167ad61bd'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import MEDIUMTEXT

def upgrade():
    op.alter_column(table_name="widget_text", column_name="text", type_=MEDIUMTEXT(charset='utf8'), nullable=True)

def downgrade():
    op.alter_column(table_name="widget_text", column_name="text", type_=sa.Text, nullable=True)