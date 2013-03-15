"""add performance list widget has kind and mask_performance_date

Revision ID: 1b9d18c1e5b1
Revises: 3207c7f80d17
Create Date: 2013-03-15 17:30:20.353915

"""

# revision identifiers, used by Alembic.
revision = '1b9d18c1e5b1'
down_revision = '3207c7f80d17'

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('widget_performancelist', sa.Column('kind', sa.Unicode(length=32), nullable=True))
    op.add_column('widget_performancelist', sa.Column('mask_performance_date', sa.Boolean(), nullable=False))
    op.execute('update widget_performancelist set kind = "fullset",  mask_performance_date = 0;')

def downgrade():
    op.drop_column('widget_performancelist', 'mask_performance_date')
    op.drop_column('widget_performancelist', 'kind')
