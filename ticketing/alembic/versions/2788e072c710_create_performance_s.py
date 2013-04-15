"""create performance_setting

Revision ID: 2788e072c710
Revises: e61547b1288
Create Date: 2013-04-15 17:43:21.553969

"""

# revision identifiers, used by Alembic.
revision = '2788e072c710'
down_revision = 'e61547b1288'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger
from sqlalchemy.dialects import mysql

def upgrade():
    op.create_table('PerformanceSetting',
                    sa.Column('id', Identifier(), nullable=False),
                    sa.Column('performance_id', Identifier(), nullable=True),
                    sa.Column('abbreviated_title', sa.Unicode(length=255), nullable=True),
                    sa.Column('subtitle', sa.Unicode(length=255), nullable=True),
                    sa.Column('note', sa.UnicodeText(), nullable=True),
                    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
                    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('0'), nullable=False),
                    sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
                    sa.ForeignKeyConstraint(['performance_id'], ['Performance.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )

def downgrade():
    op.drop_table('PerformanceSetting')
