"""create_page_format

Revision ID: a2b7618aece
Revises: 171bf9c2ca02
Create Date: 2012-09-04 08:01:29.003030

"""

# revision identifiers, used by Alembic.
revision = 'a2b7618aece'
down_revision = '171bf9c2ca02'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger

def upgrade():
    op.create_table('PageFormat',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('name', sa.Unicode(255), nullable=False),
        sa.Column('organization_id', Identifier(), nullable=True),
        sa.Column('printer_name', sa.Unicode(255), nullable=False),
        sa.Column('data', sa.String(length=65536), nullable=False, default=''),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['organization_id'], ['Organization.id'], 'PageFormat_ibfk_1', ondelete='CASCADE')
        )

def downgrade():
    op.drop_table('PageFormat')
