"""create extra mailinfo

Revision ID: 362dc10402f5
Revises: d2929a388ce
Create Date: 2012-08-22 19:48:02.905148

"""

# revision identifiers, used by Alembic.
revision = '362dc10402f5'
down_revision = 'd2929a388ce'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger

def upgrade():
    op.create_table('ExtraMailInfo',
                    sa.Column('id', Identifier, nullable=False),
                    sa.Column('organization_id', Identifier, nullable=True),
                    sa.Column('event_id', Identifier, nullable=True),
                    sa.Column('performance_id', Identifier, nullable=True),
                    sa.Column('data', sa.Unicode(65536), nullable=True),
                    sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
                    sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
                    sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
                    sa.ForeignKeyConstraint(['organization_id'], ['Organization.id'], name="extramailinfo_ibfk_1"),
                    sa.ForeignKeyConstraint(['event_id'], ['Event.id'], name="extramailinfo_ibfk_2"),
                    sa.ForeignKeyConstraint(['performance_id'], ['Performance.id'], name="extramailinfo_ibfk_3"),
                    sa.PrimaryKeyConstraint('id')
                    )

def downgrade():
    op.drop_table('ExtraMailInfo')
