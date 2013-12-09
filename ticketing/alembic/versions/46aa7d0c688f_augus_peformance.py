"""augus performance

Revision ID: 46aa7d0c688f
Revises: a4caeb81d1b
Create Date: 2013-12-09 15:50:06.426967

"""

# revision identifiers, used by Alembic.
revision = '46aa7d0c688f'
down_revision = 'a4caeb81d1b'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table(
        'AugusPerformance',
        sa.Column('id', Identifier, nullable=False, primary_key=True),
        sa.Column('code', sa.Integer, nullable=False, unique=True),
        sa.Column('augus_event_code', sa.Integer, nullable=False),
        sa.Column('performance_id', Identifier, nullable=False, unique=True),
        # for super class
        sa.Column('created_at', sa.TIMESTAMP(),
                  server_default=text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(),
                  server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),        
        )
    
    
def downgrade():
    op.drop_table('AugusPerformance')
