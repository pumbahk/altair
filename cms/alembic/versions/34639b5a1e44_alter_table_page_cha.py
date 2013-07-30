"""alter table page change column keywords

Revision ID: 34639b5a1e44
Revises: 4df15f221e78
Create Date: 2013-07-26 17:40:02.594793

"""

# revision identifiers, used by Alembic.
revision = '34639b5a1e44'
down_revision = '143c45be235a'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column(table_name="page", column_name="keywords", type_=sa.Unicode(length=500))

def downgrade():
    op.alter_column(table_name="page", column_name="keywords", type_=sa.Unicode(length=255))
