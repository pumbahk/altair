"""alter table promotion add column mobile link

Revision ID: 24f52aaf309f
Revises: 3edabd243c83
Create Date: 2014-01-14 10:36:30.075608

"""

# revision identifiers, used by Alembic.
revision = '24f52aaf309f'
down_revision = '3edabd243c83'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('promotion', sa.Column('mobile_link', sa.UnicodeText(), nullable=True))

def downgrade():
    op.drop_column('promotion', 'mobile_link')