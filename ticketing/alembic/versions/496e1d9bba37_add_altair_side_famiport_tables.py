"""add_altair_side_famiport_tables

Revision ID: 496e1d9bba37
Revises: 33471c50fbc0
Create Date: 2015-06-15 13:50:50.817140

"""

# revision identifiers, used by Alembic.
revision = '496e1d9bba37'
down_revision = '33471c50fbc0'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf
from altair.models import MutationDict, JSONEncodedDict

Identifier = sa.BigInteger


def upgrade():
    op.create_table(
        'AltairFamiPortVenue',
        sa.Column('id', Identifier, primary_key=True, autoincrement=True),
        sa.Column('organization_id', Identifier, sa.ForeignKey('Organization.id'), nullable=False),
        sa.Column('site_id', Identifier, sa.ForeignKey('Site.id'), nullable=False),
        sa.Column('famiport_venue_id', Identifier, nullable=False),
        sa.Column('name', sa.Unicode(50), nullable=False),
        sa.Column('name_kana', sa.Unicode(100), nullable=False),
        sa.Column('status', sa.Integer(), server_default=text('0')),
        sa.Column('last_reflected_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.UniqueConstraint('organization_id', 'site_id', 'famiport_venue_id')
        )
    op.create_table(
        'AltairFamiPortPerformanceGroup',
        sa.Column('id', Identifier, primary_key=True),
        sa.Column('organization_id', Identifier, sa.ForeignKey('Organization.id'), nullable=False),
        sa.Column('event_id', Identifier, sa.ForeignKey('Event.id'), nullable=False),
        sa.Column('code_1', sa.Unicode(6), nullable=False),
        sa.Column('code_2', sa.Unicode(4), nullable=False),
        sa.Column('name_1', sa.Unicode(80), nullable=False, default=u''),
        sa.Column('name_2', sa.Unicode(80), nullable=False, default=u''),
        sa.Column('sales_channel', sa.Integer, nullable=False),
        sa.Column('altair_famiport_venue_id', Identifier, sa.ForeignKey('AltairFamiPortVenue.id'), nullable=False),
        sa.Column('direct_sales_data', MutationDict.as_mutable(JSONEncodedDict(16384)).adapt(sa.UnicodeText)),
        sa.Column('status', sa.Integer(), server_default=text('0')),
        sa.Column('last_reflected_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True)
        )
    op.create_table(
        'AltairFamiPortPerformance',
        sa.Column('id', Identifier, primary_key=True, autoincrement=True),
        sa.Column('altair_famiport_performance_group_id', Identifier, sa.ForeignKey('AltairFamiPortPerformanceGroup.id', ondelete='CASCADE'), nullable=False),
        sa.Column('performance_id', Identifier, sa.ForeignKey('Performance.id'), nullable=False),
        sa.Column('code', sa.Unicode(3)),
        sa.Column('name', sa.Unicode(60)),
        sa.Column('type', sa.Integer, nullable=False),
        sa.Column('searchable', sa.Boolean, nullable=False, default=True),
        sa.Column('start_at', sa.DateTime(), nullable=True),
        sa.Column('ticket_name', sa.Unicode(20), nullable=True),
        sa.Column('status', sa.Integer(), server_default=text('0')),
        sa.Column('last_reflected_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.UniqueConstraint('performance_id')
        )
    op.create_table(
        'AltairFamiPortSalesSegmentPair',
        sa.Column('id', Identifier, primary_key=True, autoincrement=True),
        sa.Column('altair_famiport_performance_id', Identifier, sa.ForeignKey('AltairFamiPortPerformance.id'), nullable=False),
        sa.Column('code', sa.Unicode(3), nullable=False),
        sa.Column('name', sa.Unicode(40), nullable=False),
        sa.Column('seat_unselectable_sales_segment_id', Identifier, sa.ForeignKey('SalesSegment.id'), nullable=True),
        sa.Column('seat_selectable_sales_segment_id', Identifier, sa.ForeignKey('SalesSegment.id'), nullable=True),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('auth_required', sa.Boolean, nullable=False, default=False),
        sa.Column('auth_message', sa.Unicode(320), nullable=False, default=u''),
        sa.Column('status', sa.Integer(), server_default=text('0')),
        sa.Column('last_reflected_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True)
        )
    op.add_column(
        'OrganizationSetting',
        sa.Column('famiport_enabled', sa.Boolean(), nullable=False, server_default=text('FALSE'))
        )

def downgrade():
    op.drop_column('OrganizationSetting', 'famiport_enabled') 
    op.drop_table('AltairFamiPortSalesSegmentPair')
    op.drop_table('AltairFamiPortPerformance')
    op.drop_table('AltairFamiPortPerformanceGroup')
    op.drop_table('AltairFamiPortVenue')
