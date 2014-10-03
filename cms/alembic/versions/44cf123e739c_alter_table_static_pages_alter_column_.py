"""alter table static_pages alter column file_structure_text

Revision ID: 44cf123e739c
Revises: 44e62d46b3ce
Create Date: 2014-10-03 10:56:15.199371

"""

# revision identifiers, used by Alembic.
revision = '44cf123e739c'
down_revision = '2ad3940c2033'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import MEDIUMTEXT

def upgrade():
    op.alter_column(table_name="static_pages", column_name="file_structure_text", type_=MEDIUMTEXT(charset='utf8'), nullable=False)

def downgrade():
    op.alter_column(table_name="static_pages", column_name="file_structure_text", type_=sa.Text, nullable=False)
