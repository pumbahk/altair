"""Create Announce related tables

Revision ID: 4f8e39214b0f
Revises: bf2ef09ab6c
Create Date: 2016-06-06 14:19:49.817439

"""

# revision identifiers, used by Alembic.
revision = '4f8e39214b0f'
down_revision = 'bf2ef09ab6c'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table(
        'Announcement',
        sa.Column('id', Identifier(), primary_key=True),
        sa.Column('organization_id', Identifier(), sa.ForeignKey('Organization.id'), nullable=False),
        sa.Column('event_id', Identifier(), sa.ForeignKey('Event.id'), nullable=False),
        sa.Column('subject', sa.String(length=255), nullable=False),
        sa.Column('message', sa.String(length=8000), nullable=False),
        sa.Column('parameters', sa.String(length=8000), nullable=False),
        sa.Column('words', sa.String(length=1024)),
        sa.Column('send_after', sa.DateTime(), nullable=False),
        sa.Column('is_draft', sa.Boolean(), default=False),

        sa.Column('template_name', sa.String(length=64)),
        sa.Column('note', sa.String(length=1024)),
        sa.Column('started_at', sa.DateTime()),
        sa.Column('completed_at', sa.DateTime()),
        sa.Column('subscriber_count', sa.Integer()),

        sa.Column('created_at', sa.TIMESTAMP(), server_default=text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        )

    op.create_table(
        'AnnouncementTemplate',
        sa.Column('id', Identifier(), primary_key=True),
        sa.Column('organization_id', Identifier(), sa.ForeignKey('Organization.id'), nullable=False),
        sa.Column('name', sa.String(length=64), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=False),
        sa.Column('subject', sa.String(length=255), nullable=False),
        sa.Column('message', sa.String(length=8000), nullable=False),
        sa.Column('sort', sa.Integer()),
        );

def downgrade():
    op.drop_table('Announcement')
    op.drop_table('AnnouncementTempalte')
