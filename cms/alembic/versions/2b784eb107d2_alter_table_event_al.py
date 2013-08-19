"""alter table Event alter column inquiry_for

Revision ID: 2b784eb107d2
Revises: 10682b0e9b28
Create Date: 2013-08-16 17:05:45.845907

"""

# revision identifiers, used by Alembic.
revision = '2b784eb107d2'
down_revision = '10682b0e9b28'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import TEXT

def upgrade():
    op.alter_column(table_name="event", column_name="inquiry_for", type_=TEXT(charset='utf8'))

def downgrade():
    op.alter_column(table_name="event", column_name="inquiry_for", type_=sa.Unicode(length=255))

