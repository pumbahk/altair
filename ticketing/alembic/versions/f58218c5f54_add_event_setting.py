"""add_event_setting

Revision ID: f58218c5f54
Revises: 4bd1e96e03eb
Create Date: 2013-10-30 02:03:14.114740

"""

# revision identifiers, used by Alembic.
revision = 'f58218c5f54'
down_revision = '4bd1e96e03eb'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table('EventSetting',
        sa.Column('id', Identifier(), autoincrement=True),
        sa.Column('event_id', Identifier(), nullable=False),
        sa.Column('performance_selector', sa.Unicode(255)),
        sa.Column('performance_selector_label1_override', sa.Unicode(255), nullable=True),
        sa.Column('performance_selector_label2_override', sa.Unicode(255), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['event_id'], ['Event.id'], 'EventSetting_ibfk_1')
        )
    pass

def downgrade():
    op.drop_table('EventSetting')
