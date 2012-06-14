"""add column link topic

Revision ID: 49442bfedb1c
Revises: 195157f232b3
Create Date: 2012-06-14 15:10:10.115393

"""

# revision identifiers, used by Alembic.
revision = '49442bfedb1c'
down_revision = '195157f232b3'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('topcontent', sa.Column('link', sa.Unicode(length=255), nullable=True))
    op.add_column('topic', sa.Column('link', sa.Unicode(length=255), nullable=True))

def downgrade():
    op.drop_column('topic', 'link')
    op.drop_column('topcontent', 'link')
