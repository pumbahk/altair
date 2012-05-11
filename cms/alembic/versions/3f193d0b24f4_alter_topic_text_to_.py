"""alter topic.text to unicodetext

Revision ID: 3f193d0b24f4
Revises: 49a1b9ae642f
Create Date: 2012-05-11 16:46:00.413931

"""

# revision identifiers, used by Alembic.
revision = '3f193d0b24f4'
down_revision = '49a1b9ae642f'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column("topic",  "text",  type_=sa.Unicode(length=255),  existing_type=sa.UnicodeText)

def downgrade():
    op.alter_column("topic",  "text",  type_=sa.Unicode(length=255),  existing_type=sa.UnicodeText)
