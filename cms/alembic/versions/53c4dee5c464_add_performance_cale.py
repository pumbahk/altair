"""add performance.calendar_contetn

Revision ID: 53c4dee5c464
Revises: 1f10bad1f8d3
Create Date: 2012-07-09 16:25:00.876968

"""

# revision identifiers, used by Alembic.
revision = '53c4dee5c464'
down_revision = '1f10bad1f8d3'

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('performance', sa.Column('calendar_content', sa.UnicodeText(), nullable=True))

def downgrade():
    op.drop_column('performance', 'calendar_content')
