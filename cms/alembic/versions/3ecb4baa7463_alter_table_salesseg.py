"""alter table salessegment_group add column publicp

Revision ID: 3ecb4baa7463
Revises: 512e091d8fc6
Create Date: 2013-05-28 16:19:02.620546

"""

# revision identifiers, used by Alembic.
revision = '3ecb4baa7463'
down_revision = '512e091d8fc6'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('salessegment_group', sa.Column('publicp', sa.Boolean(), nullable=False, default=True))
    op.execute('UPDATE salessegment_group SET publicp = 1;')

def downgrade():
    op.drop_column('salessegment_group', 'publicp')
