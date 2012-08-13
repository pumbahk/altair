"""add save_type widget_disposition

Revision ID: 4b2e37cab469
Revises: 2a574378e873
Create Date: 2012-08-10 16:30:05.366050

"""

# revision identifiers, used by Alembic.
revision = '4b2e37cab469'
down_revision = '2a574378e873'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('widgetdisposition', sa.Column('save_type', sa.String(length=16), nullable=True))
    op.execute('update widgetdisposition set save_type = "deep";')

def downgrade():
    op.drop_column('widgetdisposition', 'save_type')
