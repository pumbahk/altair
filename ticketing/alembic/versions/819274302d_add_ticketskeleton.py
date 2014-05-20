"""add ticketskeleton

Revision ID: 819274302d
Revises: e5d3ca99cb6
Create Date: 2014-05-20 03:23:27.444495

"""

# revision identifiers, used by Alembic.
revision = '819274302d'
down_revision = 'e5d3ca99cb6'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger
from sqlalchemy.dialects import mysql

def upgrade():
    op.create_table('TicketSkeleton',
    sa.Column('id', Identifier(), nullable=False),
    sa.Column('organization_id', Identifier(), nullable=True),
    sa.Column('ticket_format_id', Identifier(), nullable=False),
    sa.Column('name', sa.Unicode(length=255), nullable=False),
    sa.Column('data', sa.String(length=65536), nullable=False, default="{}"),
    sa.Column('filename', sa.Unicode(length=255), nullable=False),
    sa.Column('cover_print', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
    sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
    sa.ForeignKeyConstraint(['organization_id'], ['Organization.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['ticket_format_id'], ['TicketFormat.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_TicketSkeleton_deleted_at', 'TicketSkeleton', ['deleted_at'], unique=False)

def downgrade():
    op.drop_table('TicketSkeleton')
    ## end Alembic commands ###
