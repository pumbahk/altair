# encoding: utf-8
"""create_famiport_related_tables

Revision ID: 2dc08c115933
Revises: 38e00b9843c3
Create Date: 2015-07-14 16:56:00.043198

"""

# revision identifiers, used by Alembic.
revision = '2dc08c115933'
down_revision = '38e00b9843c3'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf
from datetime import date, time
from altair.models import MutationDict, JSONEncodedDict

Identifier = sa.BigInteger


def upgrade():
    from altair.app.ticketing.payments.plugins import (
        FAMIPORT_PAYMENT_PLUGIN_ID,
        FAMIPORT_DELIVERY_PLUGIN_ID,
        )
    sql = u"""INSERT INTO PaymentMethodPlugin (id, name) VALUES ({plugin_id}, 'ファミポート決済') ON DUPLICATE KEY UPDATE id={plugin_id};""".format(plugin_id=FAMIPORT_PAYMENT_PLUGIN_ID)  # noqa
    op.execute(sql)
    sql = u"INSERT INTO DeliveryMethodPlugin (id, name) VALUES({plugin_id}, 'ファミポート引取') ON DUPLICATE KEY UPDATE id={plugin_id} ;".format(plugin_id=FAMIPORT_DELIVERY_PLUGIN_ID)  # noqa
    op.execute(sql)
    op.create_table(
        'FamiPortTenant',
        sa.Column('id', Identifier, autoincrement=True, primary_key=True),
        sa.Column('organization_id', Identifier, sa.ForeignKey('Organization.id')),
        sa.Column('name', sa.Unicode(255), nullable=False),
        sa.Column('code', sa.Unicode(24), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.UniqueConstraint('organization_id', 'code')
        )
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
    op.create_table(
        'FamiPortTicketTemplate',
        sa.Column('id', Identifier(), nullable=False, autoincrement=True, primary_key=True),
        sa.Column('template_code', sa.Unicode(13), nullable=False),
        sa.Column('logically_subticket', sa.Boolean(), nullable=False, server_default=text(u"FALSE")),
        sa.Column('mappings', MutationDict.as_mutable(JSONEncodedDict(16384)).adapt(sa.UnicodeText), nullable=False)
        )
    op.execute(u'''INSERT INTO FamiPortTicketTemplate (template_code, logically_subticket, mappings) VALUES ('TTTSTR0001', FALSE, '[["TitleOver", "{{{イベント名}}}"], ["TitleMain", "{{{パフォーマンス名}}}"], ["TitleSub", "{{{公演名副題}}}"], ["FreeSpace1", ""], ["FreeSpace2", ""], ["Date", "{{{開催日}}}"], ["OpenTime", "{{{開場時刻}}}"], ["StartTime", "{{{開始時刻}}}"], ["Price", "{{{チケット価格}}}"], ["Hall", "{{{会場名}}}"], ["Note1", "{{{aux.注意事項1}}}"], ["Note2", "{{{aux.注意事項2}}}"], ["Note3", "{{{aux.注意事項3}}}"], ["Note4", "{{{aux.注意事項4}}}"], ["Note5", "{{{aux.注意事項5}}}"], ["Note6", "{{{aux.注意事項6}}}"], ["Note7", "{{{aux.注意事項7}}}"], ["Seat1", "{{{券種名}}}"], ["Seat2", ""], ["Seat3", ""], ["Seat4", ""], ["Seat5", ""], ["Sub-Title1", "{{{イベント名}}}"], ["Sub-Title2", "{{{パフォーマンス名}}}"], ["Sub-Title3", "{{{公演名副題}}}"], ["Sub-Date", "{{{開催日s}}}"], ["Sub-OpenTime", "{{{開場時刻s}}}"], ["Sub-StartTime", "{{{開始時刻s}}}"], ["Sub-Price", "{{{チケット価格}}}"], ["Sub-Seat1", "{{{券種名}}}"], ["Sub-Seat2", ""], ["Sub-Seat3", ""], ["Sub-Seat4", ""], ["Sub-Seat5", ""]]')''')
    op.create_table(
        'AltairFamiPortNotification',
        sa.Column('id', Identifier, primary_key=True, autoincrement=True),
        sa.Column('type', sa.Integer, nullable=False),
        sa.Column('client_code', sa.Unicode(24), nullable=False),
        sa.Column('order_no', sa.Unicode(12), nullable=False),
        sa.Column('famiport_order_identifier', sa.Unicode(12), nullable=True),
        sa.Column('payment_reserve_number', sa.Unicode(13), nullable=True),
        sa.Column('ticketing_reserve_number', sa.Unicode(13), nullable=True),
        sa.Column('reflected_at', sa.DateTime(), nullable=True, index=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False)
        )

def downgrade():
    from altair.app.ticketing.payments.plugins import (
        FAMIPORT_PAYMENT_PLUGIN_ID,
        FAMIPORT_DELIVERY_PLUGIN_ID,
        )
    op.drop_table('AltairFamiPortNotification')
    op.drop_table('FamiPortTicketTemplate')
    op.drop_column('OrganizationSetting', 'famiport_enabled') 
    op.drop_table('AltairFamiPortSalesSegmentPair')
    op.drop_table('AltairFamiPortPerformance')
    op.drop_table('AltairFamiPortPerformanceGroup')
    op.drop_table('AltairFamiPortVenue')
    op.drop_table('FamiPortTenant')
    sql = u'DELETE FROM PaymentMethodPlugin WHERE id={plugin_id} AND (SELECT COUNT(*) FROM PaymentMethod WHERE PaymentMethod.payment_plugin_id={plugin_id}) = 0;'.format(plugin_id=FAMIPORT_PAYMENT_PLUGIN_ID)  # noqa
    op.execute(sql)
    sql = 'DELETE FROM DeliveryMethodPlugin WHERE id={plugin_id} AND (SELECT COUNT(*) FROM DeliveryMethod WHERE DeliveryMethod.delivery_plugin_id={plugin_id}) = 0;'.format(plugin_id=FAMIPORT_DELIVERY_PLUGIN_ID)  # noqa
    op.execute(sql)

