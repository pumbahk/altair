"""some widget has show_label flag.

Revision ID: 3207c7f80d17
Revises: dd1556bd98a
Create Date: 2013-03-14 17:15:32.719829

"""

# revision identifiers, used by Alembic.
revision = '3207c7f80d17'
down_revision = 'dd1556bd98a'

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('widget_calendar', sa.Column('show_label', sa.Boolean(), nullable=False, default=True))
    op.add_column('widget_summary', sa.Column('show_label', sa.Boolean(), nullable=False, default=True))
    op.add_column('widget_ticketlist', sa.Column('show_label', sa.Boolean(), nullable=False, default=True))
    op.execute("update widget_calendar set show_label=1;")
    op.execute("update widget_summary set show_label=1;")
    op.execute("update widget_ticketlist set show_label=1;")

def downgrade():
    op.drop_column('widget_ticketlist', 'show_label')
    op.drop_column('widget_summary', 'show_label')
    op.drop_column('widget_calendar', 'show_label')
