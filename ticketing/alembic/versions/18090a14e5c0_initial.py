"""
Initial table definitions

Revision ID: 18090a14e5c0
Revises: None
Create Date: 2012-07-23 12:24:01.669059

"""

# revision identifiers, used by Alembic.
revision = '18090a14e5c0'
down_revision = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf
from sqlalchemy.dialects import mysql

Identifier = sa.BigInteger

def create_master_tables():
    op.create_table('Bank',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('code', sa.BigInteger(), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('Service',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('key', sa.String(length=30), nullable=True),
        sa.Column('secret', sa.String(length=30), nullable=True),
        sa.Column('redirect_uri', sa.String(length=1024), nullable=True),
        sa.Column('status', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('secret')
        )

def create_plugin_related_tables():
    op.create_table('DeliveryMethodPlugin',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('PaymentMethodPlugin',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id')
        )

def create_organization_table():
    op.create_table('Organization',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('code', sa.String(length=3), nullable=True),
        sa.Column('client_type', sa.Integer(), nullable=True),
        sa.Column('contact_email', sa.String(length=255), nullable=True),
        sa.Column('city', sa.String(length=255), nullable=True),
        sa.Column('street', sa.String(length=255), nullable=True),
        sa.Column('address', sa.String(length=255), nullable=True),
        sa.Column('other_address', sa.String(length=255), nullable=True),
        sa.Column('tel_1', sa.String(length=32), nullable=True),
        sa.Column('tel_2', sa.String(length=32), nullable=True),
        sa.Column('fax', sa.String(length=32), nullable=True),
        sa.Column('user_id', Identifier(), nullable=True),
        sa.Column('prefecture', sa.String(length=64), nullable=False),
        sa.Column('status', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['User.id'], 'organization_ibfk_1'),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('Account',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('account_type', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('user_id', Identifier(), nullable=True),
        sa.Column('organization_id', Identifier(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['Organization.id'], 'account_ibfk_1'),
        sa.ForeignKeyConstraint(['user_id'], ['User.id'], 'account_ibfk_2'),
        sa.PrimaryKeyConstraint('id')
        )

def create_user_related_tables():
    op.create_table('BankAccount',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('bank_id', Identifier(), nullable=True),
        sa.Column('account_type', sa.Integer(), nullable=True),
        sa.Column('account_number', sa.String(length=255), nullable=True),
        sa.Column('account_owner', sa.String(length=255), nullable=True),
        sa.Column('status', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['bank_id'], ['Bank.id'], 'bankaccount_ibfk_1'),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('User',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('status', sa.Integer(), nullable=True),
        sa.Column('bank_account_id', Identifier(), nullable=True),
        sa.ForeignKeyConstraint(['bank_account_id'], ['BankAccount.id'], 'user_ibfk_1'),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('UserProfile',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('user_id', Identifier(), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('nick_name', sa.String(length=255), nullable=True),
        sa.Column('first_name', sa.String(length=255), nullable=True),
        sa.Column('last_name', sa.String(length=255), nullable=True),
        sa.Column('first_name_kana', sa.String(length=255), nullable=True),
        sa.Column('last_name_kana', sa.String(length=255), nullable=True),
        sa.Column('birth_day', sa.DateTime(), nullable=True),
        sa.Column('sex', sa.Integer(), nullable=True),
        sa.Column('zip', sa.String(length=255), nullable=True),
        sa.Column('country', sa.String(length=255), nullable=True),
        sa.Column('prefecture', sa.String(length=64), nullable=False),
        sa.Column('city', sa.String(length=255), nullable=False),
        sa.Column('address_1', sa.String(length=255), nullable=False),
        sa.Column('address_2', sa.String(length=255), nullable=True),
        sa.Column('tel_1', sa.String(length=32), nullable=True),
        sa.Column('tel_2', sa.String(length=32), nullable=True),
        sa.Column('fax', sa.String(length=32), nullable=True),
        sa.Column('status', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['User.id'], 'userprofile_ibfk_1'),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('MemberShip',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('status', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
        )

def create_mail_magazine_related_tables():
    op.create_table('MailMagazine',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('description', sa.String(length=1024), nullable=True),
        sa.Column('organization_id', Identifier(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('status', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['Organization.id'], 'mailmagazine_ibfk_1'),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('MailSubscription',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('user_id', Identifier(), nullable=True),
        sa.Column('segment_id', Identifier(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('status', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['segment_id'], ['MailMagazine.id'], 'mailsubscription_ibfk_1'),
        sa.ForeignKeyConstraint(['user_id'], ['User.id'], 'mailsubscription_ibfk_2'),
        sa.PrimaryKeyConstraint('id')
        )

def create_event_related_tables():
    op.create_table('Event',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('code', sa.String(length=12), nullable=True),
        sa.Column('title', sa.String(length=1024), nullable=True),
        sa.Column('abbreviated_title', sa.String(length=1024), nullable=True),
        sa.Column('account_id', Identifier(), nullable=True),
        sa.Column('organization_id', Identifier(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['account_id'], ['Account.id'], 'event_ibfk_1'),
        sa.ForeignKeyConstraint(['organization_id'], ['Organization.id'], 'event_ibfk_2'),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('Performance',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('code', sa.String(length=12), nullable=True),
        sa.Column('open_on', sa.DateTime(), nullable=True),
        sa.Column('start_on', sa.DateTime(), nullable=True),
        sa.Column('end_on', sa.DateTime(), nullable=True),
        sa.Column('event_id', Identifier(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['event_id'], ['Event.id'], 'performance_ibfk_1'),
        sa.PrimaryKeyConstraint('id')
        )

def create_venue_related_tables():
    op.create_table('Site',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('zip', sa.String(length=255), nullable=True),
        sa.Column('prefecture', sa.String(length=255), nullable=True),
        sa.Column('city', sa.String(length=255), nullable=True),
        sa.Column('street', sa.String(length=255), nullable=True),
        sa.Column('address', sa.String(length=255), nullable=True),
        sa.Column('other_address', sa.String(length=255), nullable=True),
        sa.Column('tel_1', sa.String(length=32), nullable=True),
        sa.Column('tel_2', sa.String(length=32), nullable=True),
        sa.Column('fax', sa.String(length=32), nullable=True),
        sa.Column('drawing_url', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('Venue',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('site_id', Identifier(), nullable=False),
        sa.Column('performance_id', Identifier(), nullable=True),
        sa.Column('organization_id', Identifier(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('sub_name', sa.String(length=255), nullable=True),
        sa.Column('original_venue_id', Identifier(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['Organization.id'], 'venue_ibfk_1'),
        sa.ForeignKeyConstraint(['original_venue_id'], ['Venue.id'], 'venue_ibfk_2'),
        sa.ForeignKeyConstraint(['performance_id'], ['Performance.id'], 'venue_ibfk_3'),
        sa.ForeignKeyConstraint(['site_id'], ['Site.id'], 'venue_ibfk_4'),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('VenueArea',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('Seat',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('l0_id', sa.String(length=255), nullable=True),
        sa.Column('name', sa.Unicode(length=50), server_default='', nullable=False),
        sa.Column('stock_id', Identifier(), nullable=True),
        sa.Column('stock_type_id', Identifier(), nullable=True),
        sa.Column('venue_id', Identifier(), nullable=False),
        sa.Column('group_l0_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.Index('ix_l0_id', 'l0_id', unique=False),
        sa.Index('ix_group_l0_id', 'group_l0_id', unique=False),
        sa.ForeignKeyConstraint(['stock_id'], ['Stock.id'], 'seat_ibfk_1'),
        sa.ForeignKeyConstraint(['stock_type_id'], ['StockType.id'], 'seat_ibfk_2'),
        sa.ForeignKeyConstraint(['venue_id'], ['Venue.id'], 'seat_ibfk_3'),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('SeatAdjacencySet',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('venue_id', Identifier(), nullable=True),
        sa.Column('seat_count', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['venue_id'], ['Venue.id'], 'seatadjacencyset_ibfk_1'),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('SeatAdjacency',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('adjacency_set_id', Identifier(), nullable=True),
        sa.ForeignKeyConstraint(['adjacency_set_id'], ['SeatAdjacencySet.id'], 'seatadjacency_ibfk_1'),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('Seat_SeatAdjacency',
        sa.Column('seat_id', Identifier(), nullable=False),
        sa.Column('seat_adjacency_id', Identifier(), nullable=False),
        sa.ForeignKeyConstraint(['seat_adjacency_id'], ['SeatAdjacency.id'], 'seat_seatadjacency_ibfk_1'),
        sa.ForeignKeyConstraint(['seat_id'], ['Seat.id'], 'seat_seatadjacency_ibfk_2'),
        sa.PrimaryKeyConstraint('seat_id', 'seat_adjacency_id')
        )
    op.create_table('SeatStatus',
        sa.Column('seat_id', Identifier(), nullable=False),
        sa.Column('status', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['seat_id'], ['Seat.id'], 'seatstatus_ibfk_1'),
        sa.PrimaryKeyConstraint('seat_id')
        )
    op.create_table('SeatAttribute',
        sa.Column('seat_id', Identifier(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('value', sa.String(length=1023), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['seat_id'], ['Seat.id'], 'seatattribute_ibfk_1'),
        sa.PrimaryKeyConstraint('seat_id', 'name')
        )
    op.create_table('SeatIndexType',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('venue_id', Identifier(), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['venue_id'], ['Venue.id'], 'seatindextype_ibfk_1'),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('SeatIndex',
        sa.Column('seat_index_type_id', Identifier(), nullable=False),
        sa.Column('seat_id', Identifier(), nullable=False),
        sa.Column('index', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['seat_id'], ['Seat.id'], 'seatindex_ibfk_1'),
        sa.ForeignKeyConstraint(['seat_index_type_id'], ['SeatIndexType.id'], 'seatindex_ibfk_2'),
        sa.PrimaryKeyConstraint('seat_index_type_id', 'seat_id')
        )
    op.create_table('VenueArea_group_l0_id',
        sa.Column('venue_id', Identifier(), nullable=False),
        sa.Column('group_l0_id', sa.String(length=255), nullable=True),
        sa.Column('venue_area_id', Identifier(), nullable=False),
        sa.ForeignKeyConstraint(['group_l0_id'], ['Seat.group_l0_id'], 'venuearea_group_l0_id_ibfk_1'),
        sa.ForeignKeyConstraint(['venue_area_id'], ['VenueArea.id'], 'venuearea_group_l0_id_ibfk_2'),
        sa.ForeignKeyConstraint(['venue_id'], ['Venue.id'], 'venuearea_group_l0_id_ibfk_3'),
        sa.PrimaryKeyConstraint('venue_id', 'group_l0_id', 'venue_area_id')
        )

def create_sales_related_tables():
    op.create_table('PaymentMethod',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('fee', sa.Numeric(precision=16, scale=2), nullable=False),
        sa.Column('fee_type', sa.Integer(), nullable=False),
        sa.Column('organization_id', Identifier(), nullable=True),
        sa.Column('payment_plugin_id', Identifier(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['Organization.id'], 'paymentmethod_ibfk_1'),
        sa.ForeignKeyConstraint(['payment_plugin_id'], ['PaymentMethodPlugin.id'], 'paymentmethod_ibfk_2'),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('DeliveryMethod',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('fee', sa.Numeric(precision=16, scale=2), nullable=False),
        sa.Column('fee_type', sa.Integer(), nullable=False),
        sa.Column('organization_id', Identifier(), nullable=True),
        sa.Column('delivery_plugin_id', Identifier(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['delivery_plugin_id'], ['DeliveryMethodPlugin.id'], 'deliverymethod_ibfk_1'),
        sa.ForeignKeyConstraint(['organization_id'], ['Organization.id'], 'deliverymethod_ibfk_2'),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('SalesSegment',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('kind', sa.String(length=255), nullable=True),
        sa.Column('start_at', sa.DateTime(), nullable=True),
        sa.Column('end_at', sa.DateTime(), nullable=True),
        sa.Column('upper_limit', sa.Integer(), nullable=True),
        sa.Column('seat_choice', sa.Boolean(), nullable=True),
        sa.Column('event_id', Identifier(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.CheckConstraint('TODO'),
        sa.ForeignKeyConstraint(['event_id'], ['Event.id'], 'salessegment_ibfk_1'),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('PaymentDeliveryMethodPair',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('system_fee', sa.Numeric(precision=16, scale=2), nullable=False),
        sa.Column('transaction_fee', sa.Numeric(precision=16, scale=2), nullable=False),
        sa.Column('delivery_fee', sa.Numeric(precision=16, scale=2), nullable=False),
        sa.Column('discount', sa.Numeric(precision=16, scale=2), nullable=False),
        sa.Column('discount_unit', sa.Integer(), nullable=True),
        sa.Column('payment_period_days', sa.Integer(), nullable=True),
        sa.Column('issuing_interval_days', sa.Integer(), nullable=True),
        sa.Column('issuing_start_at', sa.DateTime(), nullable=True),
        sa.Column('issuing_end_at', sa.DateTime(), nullable=True),
        sa.Column('sales_segment_id', Identifier(), nullable=True),
        sa.Column('payment_method_id', Identifier(), nullable=True),
        sa.Column('delivery_method_id', Identifier(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['delivery_method_id'], ['DeliveryMethod.id'], 'paymentdeliverymethodpair_ibfk_1'),
        sa.ForeignKeyConstraint(['payment_method_id'], ['PaymentMethod.id'], 'paymentdeliverymethodpair_ibfk_2'),
        sa.ForeignKeyConstraint(['sales_segment_id'], ['SalesSegment.id'], 'paymentdeliverymethodpair_ibfk_3'),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('StockType',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('type', sa.Integer(), nullable=True),
        sa.Column('event_id', Identifier(), nullable=True),
        sa.Column('quantity_only', sa.Boolean(), nullable=True),
        sa.Column('style', sa.String(length=1024), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.CheckConstraint('TODO'),
        sa.ForeignKeyConstraint(['event_id'], ['Event.id'], 'stocktype_ibfk_1'),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('StockAllocation',
        sa.Column('stock_type_id', Identifier(), nullable=False),
        sa.Column('performance_id', Identifier(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['performance_id'], ['Performance.id'], 'stockallocation_ibfk_1'),
        sa.ForeignKeyConstraint(['stock_type_id'], ['StockType.id'], 'stockallocation_ibfk_2'),
        sa.PrimaryKeyConstraint('stock_type_id', 'performance_id')
        )
    op.create_table('StockHolder',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('event_id', Identifier(), nullable=True),
        sa.Column('account_id', Identifier(), nullable=True),
        sa.Column('style', sa.String(length=1024), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['account_id'], ['Account.id'], 'stockholder_ibfk_1'),
        sa.ForeignKeyConstraint(['event_id'], ['Event.id'], 'stockholder_ibfk_2'),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('Stock',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=True),
        sa.Column('performance_id', Identifier(), nullable=True),
        sa.Column('stock_holder_id', Identifier(), nullable=True),
        sa.Column('stock_type_id', Identifier(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['performance_id'], ['Performance.id'], 'stock_ibfk_1'),
        sa.ForeignKeyConstraint(['stock_holder_id'], ['StockHolder.id'], 'stock_ibfk_2'),
        sa.ForeignKeyConstraint(['stock_type_id'], ['StockType.id'], 'stock_ibfk_3'),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('StockStatus',
        sa.Column('stock_id', Identifier(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['stock_id'], ['Stock.id'], 'stockstatus_ibfk_1'),
        sa.PrimaryKeyConstraint('stock_id')
        )
    op.create_table('Product',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('price', sa.Numeric(precision=16, scale=2), nullable=False),
        sa.Column('sales_segment_id', Identifier(), nullable=True),
        sa.Column('event_id', Identifier(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['event_id'], ['Event.id'], 'product_ibfk_1'),
        sa.ForeignKeyConstraint(['sales_segment_id'], ['SalesSegment.id'], 'product_ibfk_2'),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('ProductItem',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('item_type', sa.Integer(), nullable=True),
        sa.Column('price', sa.Numeric(precision=16, scale=2), nullable=False),
        sa.Column('product_id', Identifier(), nullable=True),
        sa.Column('performance_id', Identifier(), nullable=True),
        sa.Column('stock_id', Identifier(), nullable=True),
        sa.Column('quantity', sa.Integer(), server_default='1', nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['performance_id'], ['Performance.id'], 'productitem_ibfk_1'),
        sa.ForeignKeyConstraint(['product_id'], ['Product.id'], 'productitem_ibfk_2'),
        sa.ForeignKeyConstraint(['stock_id'], ['Stock.id'], 'productitem_ibfk_3'),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('BuyerCondition',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('membership_id', Identifier(), nullable=True),
        sa.ForeignKeyConstraint(['membership_id'], ['MemberShip.id'], 'buyercondition_ibfk_1'),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('BuyerConditionSet',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('buyer_condition_id', Identifier(), nullable=True),
        sa.Column('product_id', Identifier(), nullable=True),
        sa.ForeignKeyConstraint(['buyer_condition_id'], ['BuyerCondition.id'], 'buyerconditionset_ibfk_1'),
        sa.ForeignKeyConstraint(['product_id'], ['Product.id'], 'buyerconditionset_ibfk_2'),
        sa.PrimaryKeyConstraint('id')
        )

def create_checkout_related_tables():
    op.create_table('Checkout',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('orderId', sa.Unicode(length=30), nullable=True),
        sa.Column('orderControlId', sa.Unicode(length=31), nullable=True),
        sa.Column('orderCartId', sa.Unicode(length=255), nullable=True),
        sa.Column('openId', sa.Unicode(length=128), nullable=True),
        sa.Column('isTMode', sa.Enum('0', '1'), nullable=True),
        sa.Column('usedPoint', sa.Integer(), nullable=True),
        sa.Column('orderTotalFee', sa.Integer(), nullable=True),
        sa.Column('orderDate', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.CheckConstraint('TODO'),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('CheckoutItem',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('checkout_id', sa.Integer(), nullable=True),
        sa.Column('itemId', sa.String(length=100), nullable=True),
        sa.Column('itemName', sa.Unicode(length=255), nullable=True),
        sa.Column('itemNumbers', sa.Integer(), nullable=True),
        sa.Column('itemFee', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['checkout_id'], ['Checkout.id'], 'checkoutitem_ibfk_1'),
        sa.PrimaryKeyConstraint('id')
        )

def create_multicheckout_related_tables():
    op.create_table('multicheckout_request_card',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ItemCd', sa.Unicode(length=3), nullable=True),
        sa.Column('ItemName', sa.Unicode(length=44), nullable=True),
        sa.Column('OrderYMD', sa.Unicode(length=8), nullable=True),
        sa.Column('SalesAmount', sa.Integer(), nullable=True),
        sa.Column('TaxCarriage', sa.Integer(), nullable=True),
        sa.Column('FreeData', sa.Unicode(length=32), nullable=True),
        sa.Column('ClientName', sa.Unicode(length=40), nullable=True),
        sa.Column('MailAddress', sa.Unicode(length=100), nullable=True),
        sa.Column('MailSend', sa.Unicode(length=1), nullable=True),
        sa.Column('CardNo', sa.Unicode(length=16), nullable=True),
        sa.Column('CardLimit', sa.Unicode(length=4), nullable=True),
        sa.Column('CardHolderName', sa.Unicode(length=42), nullable=True),
        sa.Column('PayKindCd', sa.Unicode(length=2), nullable=True),
        sa.Column('PayCount', sa.Integer(), nullable=True),
        sa.Column('SecureKind', sa.Unicode(length=1), nullable=True),
        sa.Column('SecureCode', sa.Unicode(length=4), nullable=True),
        sa.Column('Mvn', sa.Unicode(length=10), nullable=True),
        sa.Column('Xid', sa.Unicode(length=28), nullable=True),
        sa.Column('Ts', sa.Unicode(length=1), nullable=True),
        sa.Column('ECI', sa.Unicode(length=2), nullable=True),
        sa.Column('CAVV', sa.Unicode(length=28), nullable=True),
        sa.Column('CavvAlgorithm', sa.Unicode(length=1), nullable=True),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('multicheckout_response_card',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('BizClassCd', sa.Unicode(length=2), nullable=True),
        sa.Column('Storecd', sa.Unicode(length=10), nullable=True),
        sa.Column('OrderNo', sa.Unicode(length=32), nullable=True),
        sa.Column('Status', sa.Unicode(length=3), nullable=True),
        sa.Column('PublicTranId', sa.Unicode(length=25), nullable=True),
        sa.Column('AheadComCd', sa.Unicode(length=7), nullable=True),
        sa.Column('ApprovalNo', sa.Unicode(length=7), nullable=True),
        sa.Column('CardErrorCd', sa.Unicode(length=6), nullable=True),
        sa.Column('ReqYmd', sa.Unicode(length=8), nullable=True),
        sa.Column('CmnErrorCd', sa.Unicode(length=6), nullable=True),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('multicheckout_inquiry_response_card',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('Storecd', sa.Unicode(length=10), nullable=True),
        sa.Column('EventDate', sa.Unicode(length=14), nullable=True),
        sa.Column('Status', sa.Unicode(length=3), nullable=True),
        sa.Column('CardErrorCd', sa.Unicode(length=6), nullable=True),
        sa.Column('ApprovalNo', sa.Unicode(length=7), nullable=True),
        sa.Column('CmnErrorCd', sa.Unicode(length=6), nullable=True),
        sa.Column('OrderNo', sa.Unicode(length=32), nullable=True),
        sa.Column('ItemName', sa.Unicode(length=44), nullable=True),
        sa.Column('OrderYMD', sa.Unicode(length=8), nullable=True),
        sa.Column('SalesAmount', sa.Integer(), nullable=True),
        sa.Column('FreeData', sa.Unicode(length=32), nullable=True),
        sa.Column('ClientName', sa.Unicode(length=40), nullable=True),
        sa.Column('MailAddress', sa.Unicode(length=100), nullable=True),
        sa.Column('MailSend', sa.Unicode(length=1), nullable=True),
        sa.Column('CardNo', sa.Unicode(length=16), nullable=True),
        sa.Column('CardLimit', sa.Unicode(length=4), nullable=True),
        sa.Column('CardHolderName', sa.Unicode(length=42), nullable=True),
        sa.Column('PayKindCd', sa.Unicode(length=2), nullable=True),
        sa.Column('PayCount', sa.Integer(), nullable=True),
        sa.Column('SecureKind', sa.Unicode(length=1), nullable=True),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('multicheckout_inquiry_response_card_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('BizClassCd', sa.Unicode(length=2), nullable=True),
        sa.Column('EventDate', sa.Unicode(length=14), nullable=True),
        sa.Column('SalesAmount', sa.Unicode(length=7), nullable=True),
        sa.Column('inquiry_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['inquiry_id'], ['multicheckout_inquiry_response_card.id'], 'multicheckout_inquiry_response_card_history_ibfk_1'),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('secure3d_req_auth_request',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('Md', sa.UnicodeText(), nullable=True),
        sa.Column('PaRes', sa.UnicodeText(), nullable=True),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('secure3d_req_auth_response',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ErrorCd', sa.Unicode(length=6), nullable=True),
        sa.Column('RetCd', sa.Unicode(length=1), nullable=True),
        sa.Column('Xid', sa.Unicode(length=28), nullable=True),
        sa.Column('Ts', sa.Unicode(length=1), nullable=True),
        sa.Column('Cavva', sa.Unicode(length=1), nullable=True),
        sa.Column('Cavv', sa.Unicode(length=28), nullable=True),
        sa.Column('Eci', sa.Unicode(length=2), nullable=True),
        sa.Column('Mvn', sa.Unicode(length=10), nullable=True),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('secure3d_req_enrol_request',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('CardNumber', sa.Unicode(length=16), nullable=True),
        sa.Column('ExpYear', sa.Unicode(length=2), nullable=True),
        sa.Column('ExpMonth', sa.Unicode(length=2), nullable=True),
        sa.Column('TotalAmount', sa.Integer(), nullable=True),
        sa.Column('Currency', sa.Unicode(length=3), nullable=True),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('secure3d_req_enrol_response',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('Md', sa.UnicodeText(), nullable=True),
        sa.Column('ErrorCd', sa.Unicode(length=6), nullable=True),
        sa.Column('RetCd', sa.Unicode(length=1), nullable=True),
        sa.Column('AcsUrl', sa.UnicodeText(), nullable=True),
        sa.Column('PaReq', sa.UnicodeText(), nullable=True),
        sa.PrimaryKeyConstraint('id')
        )

def create_sej_related_tables():
    op.create_table('SejOrder',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('shop_id', sa.String(length=5), nullable=True),
        sa.Column('shop_name', sa.String(length=64), nullable=True),
        sa.Column('contact_01', sa.String(length=64), nullable=True),
        sa.Column('contact_02', sa.String(length=64), nullable=True),
        sa.Column('user_name', sa.String(length=40), nullable=True),
        sa.Column('user_name_kana', sa.String(length=40), nullable=True),
        sa.Column('tel', sa.String(length=12), nullable=True),
        sa.Column('zip_code', sa.String(length=7), nullable=True),
        sa.Column('email', sa.String(length=64), nullable=True),
        sa.Column('order_id', sa.String(length=12), nullable=True),
        sa.Column('exchange_number', sa.String(length=13), nullable=True),
        sa.Column('billing_number', sa.String(length=13), nullable=True),
        sa.Column('exchange_sheet_url', sa.String(length=128), nullable=True),
        sa.Column('exchange_sheet_number', sa.String(length=32), nullable=True),
        sa.Column('total_price', sa.DECIMAL(), nullable=True),
        sa.Column('ticket_price', sa.DECIMAL(), nullable=True),
        sa.Column('commission_fee', sa.DECIMAL(), nullable=True),
        sa.Column('ticketing_fee', sa.DECIMAL(), nullable=True),
        sa.Column('total_ticket_count', sa.Integer(), nullable=True),
        sa.Column('ticket_count', sa.Integer(), nullable=True),
        sa.Column('return_ticket_count', sa.Integer(), nullable=True),
        sa.Column('process_id', sa.String(length=12), nullable=True),
        sa.Column('payment_type', sa.Enum('1', '2', '3', '4'), nullable=True),
        sa.Column('pay_store_number', sa.String(length=6), nullable=True),
        sa.Column('pay_store_name', sa.String(length=36), nullable=True),
        sa.Column('cancel_reason', sa.String(length=2), nullable=True),
        sa.Column('ticketing_store_number', sa.String(length=6), nullable=True),
        sa.Column('ticketing_store_name', sa.String(length=36), nullable=True),
        sa.Column('payment_due_at', sa.DateTime(), nullable=True),
        sa.Column('ticketing_start_at', sa.DateTime(), nullable=True),
        sa.Column('ticketing_due_at', sa.DateTime(), nullable=True),
        sa.Column('regrant_number_due_at', sa.DateTime(), nullable=True),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.Column('order_at', sa.DateTime(), nullable=True),
        sa.Column('pay_at', sa.DateTime(), nullable=True),
        sa.Column('issue_at', sa.DateTime(), nullable=True),
        sa.Column('cancel_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.CheckConstraint('TODO'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('SejTicketTemplateFile',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('status', sa.Enum('1', '2', '3', '4'), nullable=True),
        sa.Column('template_id', sa.String(length=200), nullable=True),
        sa.Column('template_name', sa.String(length=36), nullable=True),
        sa.Column('ticket_html', sa.Binary(), nullable=True),
        sa.Column('ticket_css', sa.Binary(), nullable=True),
        sa.Column('publish_start_date', sa.Date(), nullable=True),
        sa.Column('publish_end_date', sa.Date(), nullable=True),
        sa.Column('send_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.CheckConstraint('TODO'),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('SejNotification',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('notification_type', sa.Enum('1', '31', '72', '73'), nullable=True),
        sa.Column('process_number', sa.String(length=12), nullable=True),
        sa.Column('payment_type', sa.Enum('1', '2', '3', '4'), nullable=True),
        sa.Column('payment_type_new', sa.Enum('1', '2', '3', '4'), nullable=True),
        sa.Column('shop_id', sa.String(length=5), nullable=True),
        sa.Column('order_id', sa.String(length=12), nullable=True),
        sa.Column('exchange_number', sa.String(length=13), nullable=True),
        sa.Column('exchange_number_new', sa.String(length=13), nullable=True),
        sa.Column('billing_number', sa.String(length=13), nullable=True),
        sa.Column('billing_number_new', sa.String(length=13), nullable=True),
        sa.Column('exchange_sheet_url', sa.String(length=128), nullable=True),
        sa.Column('exchange_sheet_number', sa.String(length=32), nullable=True),
        sa.Column('total_price', sa.DECIMAL(), nullable=True),
        sa.Column('total_ticket_count', sa.Integer(), nullable=True),
        sa.Column('ticket_count', sa.Integer(), nullable=True),
        sa.Column('return_ticket_count', sa.Integer(), nullable=True),
        sa.Column('ticketing_due_datetime', sa.DateTime(), nullable=True),
        sa.Column('ticketing_due_datetime_new', sa.DateTime(), nullable=True),
        sa.Column('pay_store_number', sa.String(length=6), nullable=True),
        sa.Column('pay_store_name', sa.String(length=36), nullable=True),
        sa.Column('ticketing_store_number', sa.String(length=6), nullable=True),
        sa.Column('ticketing_store_name', sa.String(length=36), nullable=True),
        sa.Column('cancel_reason', sa.String(length=2), nullable=True),
        sa.Column('barcode_numbers', sa.String(length=4096), nullable=True),
        sa.Column('reflected_at', sa.DateTime(), nullable=True),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.Column('signature', sa.String(length=32), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.CheckConstraint('TODO'),
        sa.CheckConstraint('TODO'),
        sa.CheckConstraint('TODO'),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('SejRefundEvent',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('available', sa.Integer(), nullable=True),
        sa.Column('shop_id', sa.String(length=5), nullable=True),
        sa.Column('event_code_01', sa.String(length=16), nullable=True),
        sa.Column('event_code_02', sa.String(length=16), nullable=True),
        sa.Column('title', sa.String(length=200), nullable=True),
        sa.Column('sub_title', sa.String(length=600), nullable=True),
        sa.Column('event_at', sa.DateTime(), nullable=True),
        sa.Column('start_at', sa.DateTime(), nullable=True),
        sa.Column('end_at', sa.DateTime(), nullable=True),
        sa.Column('event_expire_at', sa.DateTime(), nullable=True),
        sa.Column('ticket_expire_at', sa.DateTime(), nullable=True),
        sa.Column('refund_enabled', sa.Integer(), nullable=True),
        sa.Column('disapproval_reason', sa.Integer(), nullable=True),
        sa.Column('need_stub', sa.Integer(), nullable=True),
        sa.Column('remarks', sa.String(length=256), nullable=True),
        sa.Column('un_use_01', sa.String(length=64), nullable=True),
        sa.Column('un_use_02', sa.String(length=64), nullable=True),
        sa.Column('un_use_03', sa.String(length=64), nullable=True),
        sa.Column('un_use_04', sa.String(length=64), nullable=True),
        sa.Column('un_use_05', sa.String(length=64), nullable=True),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('SejFile',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('notification_type', sa.Enum('94', '51', '61', '92', '94', '95', '96'), nullable=True),
        sa.Column('file_date', sa.Date(), nullable=True),
        sa.Column('reflected_at', sa.DateTime(), nullable=True),
        sa.Column('file_url', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.CheckConstraint('TODO'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('file_date')
        )
    op.create_table('SejRefundTicket',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('refund_event_id', Identifier(), nullable=True),
        sa.Column('available', sa.Integer(), nullable=True),
        sa.Column('event_code_01', sa.String(length=16), nullable=True),
        sa.Column('event_code_02', sa.String(length=16), nullable=True),
        sa.Column('order_id', sa.String(length=12), nullable=True),
        sa.Column('ticket_barcode_number', sa.String(length=13), nullable=True),
        sa.Column('refund_ticket_amount', sa.DECIMAL(), nullable=True),
        sa.Column('refund_other_amount', sa.DECIMAL(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['refund_event_id'], ['SejRefundEvent.id'], 'sejrefundticket_ibfk_1'),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('SejTicket',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticket_type', sa.Enum('1', '2', '3', '4'), nullable=True),
        sa.Column('barcode_number', sa.String(length=13), nullable=True),
        sa.Column('event_name', sa.String(length=40), nullable=True),
        sa.Column('performance_name', sa.String(length=40), nullable=True),
        sa.Column('performance_datetime', sa.DateTime(), nullable=True),
        sa.Column('ticket_template_id', sa.String(length=10), nullable=True),
        sa.Column('ticket_data_xml', sa.String(length=5000), nullable=True),
        sa.Column('order_id', Identifier(), nullable=True),
        sa.Column('ticket_idx', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.CheckConstraint('TODO'),
        sa.ForeignKeyConstraint(['order_id'], ['SejOrder.id'], 'sejticket_ibfk_1'),
        sa.PrimaryKeyConstraint('id')
        )

def create_point_related_tables():
    op.create_table('UserPointAccount',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('user_id', Identifier(), nullable=True),
        sa.Column('point_type_code', sa.Integer(), nullable=True),
        sa.Column('account_number', sa.String(length=255), nullable=True),
        sa.Column('account_expire', sa.String(length=255), nullable=True),
        sa.Column('account_owner', sa.String(length=255), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('status', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['User.id'], 'userpointaccount_ibfk_1'),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('UserPointHistory',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('user_point_account_id', Identifier(), nullable=True),
        sa.Column('user_id', Identifier(), nullable=True),
        sa.Column('point', sa.Integer(), nullable=True),
        sa.Column('rate', sa.Integer(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('status', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['User.id'], 'userpointhistory_ibfk_1'),
        sa.ForeignKeyConstraint(['user_point_account_id'], ['UserPointAccount.id'], 'userpointhistory_ibfk_2'),
        sa.PrimaryKeyConstraint('id')
        )

def create_cart_related_tables():
    op.create_table('ticketing_carts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cart_session_id', sa.Unicode(length=255), nullable=True),
        sa.Column('performance_id', Identifier(), nullable=True),
        sa.Column('system_fee', sa.Numeric(precision=16, scale=2), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('finished_at', sa.DateTime(), nullable=True),
        sa.Column('shipping_address_id', Identifier(), nullable=False),
        sa.Column('payment_delivery_method_pair_id', Identifier(), nullable=True),
        sa.Index('ix_cart_session_id', 'cart_session_id'),
        sa.ForeignKeyConstraint(['payment_delivery_method_pair_id'], ['PaymentDeliveryMethodPair.id'], 'ticketing_carts_ibfk_1'),
        sa.ForeignKeyConstraint(['performance_id'], ['Performance.id'], 'ticketing_carts_ibfk_2'),
        sa.ForeignKeyConstraint(['shipping_address_id'], ['ShippingAddress.id'], 'ticketing_carts_ibfk_3'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('cart_session_id')
        )
    op.create_table('ticketing_cartedproducts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=True),
        sa.Column('cart_id', sa.Integer(), nullable=True),
        sa.Column('product_id', Identifier(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('finished_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['cart_id'], ['ticketing_carts.id'], 'ticketing_cartedproducts_ibfk_1'),
        sa.ForeignKeyConstraint(['product_id'], ['Product.id'], 'ticketing_cartedproducts_ibfk_2'),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('ticketing_cartedproductitems',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=True),
        sa.Column('product_item_id', Identifier(), nullable=True),
        sa.Column('carted_product_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('finished_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['carted_product_id'], ['ticketing_cartedproducts.id'], 'ticketing_cartedproductitems_ibfk_1'),
        sa.ForeignKeyConstraint(['product_item_id'], ['ProductItem.id'], 'ticketing_cartedproductitems_ibfk_2'),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('cat_seat',
        sa.Column('seat_id', Identifier(), nullable=True),
        sa.Column('cartproductitem_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['cartproductitem_id'], ['ticketing_cartedproductitems.id'], 'cat_seat_ibfk_1'),
        sa.ForeignKeyConstraint(['seat_id'], ['Seat.id'], 'cat_seat_ibfk_2'),
        sa.PrimaryKeyConstraint()
        )

def create_order_related_tables():
    op.create_table('ShippingAddress',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('user_id', Identifier(), nullable=True),
        sa.Column('nick_name', sa.String(length=255), nullable=True),
        sa.Column('first_name', sa.String(length=255), nullable=True),
        sa.Column('last_name', sa.String(length=255), nullable=True),
        sa.Column('first_name_kana', sa.String(length=255), nullable=True),
        sa.Column('last_name_kana', sa.String(length=255), nullable=True),
        sa.Column('sex', sa.Integer(), nullable=True),
        sa.Column('zip', sa.String(length=255), nullable=True),
        sa.Column('country', sa.String(length=255), nullable=True),
        sa.Column('prefecture', sa.String(length=255), nullable=False),
        sa.Column('city', sa.String(length=255), nullable=False),
        sa.Column('address_1', sa.String(length=255), nullable=False),
        sa.Column('address_2', sa.String(length=255), nullable=True),
        sa.Column('tel_1', sa.String(length=32), nullable=True),
        sa.Column('tel_2', sa.String(length=32), nullable=True),
        sa.Column('fax', sa.String(length=32), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['User.id'], 'shippingaddress_ibfk_1'),
        sa.PrimaryKeyConstraint('id')
        )

    op.create_table('Order',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('user_id', Identifier(), nullable=True),
        sa.Column('shipping_address_id', Identifier(), nullable=True),
        sa.Column('organization_id', Identifier(), nullable=True),
        sa.Column('total_amount', sa.Numeric(precision=16, scale=2), nullable=False),
        sa.Column('system_fee', sa.Numeric(precision=16, scale=2), nullable=False),
        sa.Column('transaction_fee', sa.Numeric(precision=16, scale=2), nullable=False),
        sa.Column('delivery_fee', sa.Numeric(precision=16, scale=2), nullable=False),
        sa.Column('multicheckout_approval_no', sa.Unicode(length=255), nullable=True),
        sa.Column('payment_delivery_method_pair_id', Identifier(), nullable=True),
        sa.Column('paid_at', sa.DateTime(), nullable=True),
        sa.Column('delivered_at', sa.DateTime(), nullable=True),
        sa.Column('canceled_at', sa.DateTime(), nullable=True),
        sa.Column('order_no', sa.String(length=255), nullable=True),
        sa.Column('performance_id', Identifier(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['Organization.id'], 'order_ibfk_1'),
        sa.ForeignKeyConstraint(['payment_delivery_method_pair_id'], ['PaymentDeliveryMethodPair.id'], 'order_ibfk_2'),
        sa.ForeignKeyConstraint(['performance_id'], ['Performance.id'], 'order_ibfk_3'),
        sa.ForeignKeyConstraint(['shipping_address_id'], ['ShippingAddress.id'], 'order_ibfk_4'),
        sa.ForeignKeyConstraint(['user_id'], ['User.id'], 'order_ibfk_5'),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('OrderedProduct',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('order_id', Identifier(), nullable=True),
        sa.Column('product_id', Identifier(), nullable=True),
        sa.Column('price', sa.Numeric(precision=16, scale=2), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['order_id'], ['Order.id'], 'orderedproduct_ibfk_1'),
        sa.ForeignKeyConstraint(['product_id'], ['Product.id'], 'orderedproduct_ibfk_2'),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('OrderedProductItem',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('ordered_product_id', Identifier(), nullable=True),
        sa.Column('product_item_id', Identifier(), nullable=True),
        sa.Column('price', sa.Numeric(precision=16, scale=2), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['ordered_product_id'], ['OrderedProduct.id'], 'orderedproductitem_ibfk_1'),
        sa.ForeignKeyConstraint(['product_item_id'], ['ProductItem.id'], 'orderedproductitem_ibfk_2'),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('orders_seat',
        sa.Column('seat_id', Identifier(), nullable=True),
        sa.Column('OrderedProductItem_id', Identifier(), nullable=True),
        sa.ForeignKeyConstraint(['OrderedProductItem_id'], ['OrderedProductItem.id'], 'orders_seat_ibfk_1'),
        sa.ForeignKeyConstraint(['seat_id'], ['Seat.id'], 'orders_seat_ibfk_2'),
        sa.PrimaryKeyConstraint()
        )
    op.create_table('OrderedProductAttribute',
        sa.Column('ordered_product_item_id', Identifier(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('value', sa.String(length=1023), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['ordered_product_item_id'], ['OrderedProductItem.id'], 'orderedproductattribute_ibfk_1'),
        sa.PrimaryKeyConstraint('ordered_product_item_id', 'name')
        )
    op.create_table('payment_reserved_number',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_no', sa.Unicode(length=255), nullable=True),
        sa.Column('number', sa.Unicode(length=32), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('order_no')
        )
    op.create_table('reserved_number',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_no', sa.Unicode(length=255), nullable=True),
        sa.Column('number', sa.Unicode(length=32), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('order_no')
        )

def create_auth_related_tables():
    op.create_table('Operator',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('organization_id', Identifier(), nullable=True),
        sa.Column('expire_at', sa.DateTime(), nullable=True),
        sa.Column('status', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['Organization.id'], 'operator_ibfk_1'),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('OperatorRole',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('status', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('Permission',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('operator_role_id', Identifier(), nullable=True),
        sa.Column('category_name', sa.String(length=255), nullable=True),
        sa.Column('permit', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['operator_role_id'], ['OperatorRole.id'], 'permission_ibfk_1'),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('OperatorRole_Operator',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('operator_role_id', Identifier(), nullable=True),
        sa.Column('operator_id', Identifier(), nullable=True),
        sa.ForeignKeyConstraint(['operator_id'], ['Operator.id'], 'operatorrole_operator_ibfk_1'),
        sa.ForeignKeyConstraint(['operator_role_id'], ['OperatorRole.id'], 'operatorrole_operator_ibfk_2'),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('UserCredential',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('auth_identifier', sa.String(length=255), nullable=True),
        sa.Column('auth_secret', sa.String(length=255), nullable=True),
        sa.Column('user_id', Identifier(), nullable=True),
        sa.Column('membership_id', Identifier(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('status', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['membership_id'], ['MemberShip.id'], 'usercredential_ibfk_1'),
        sa.ForeignKeyConstraint(['user_id'], ['User.id'], 'usercredential_ibfk_2'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('auth_identifier')
        )
    op.create_table('AccessToken',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('service_id', Identifier(), nullable=True),
        sa.Column('operator_id', Identifier(), nullable=True),
        sa.Column('key', sa.String(length=30), nullable=True),
        sa.Column('token', sa.String(length=10), nullable=True),
        sa.Column('refresh_token', sa.String(length=10), nullable=True),
        sa.Column('mac_key', sa.String(length=20), nullable=True),
        sa.Column('issue', sa.Integer(), nullable=True),
        sa.Column('expire', sa.DateTime(), nullable=True),
        sa.Column('refreshable', sa.Boolean(), nullable=True),
        sa.Column('status', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.CheckConstraint('TODO'),
        sa.ForeignKeyConstraint(['operator_id'], ['Operator.id'], 'accesstoken_ibfk_1'),
        sa.ForeignKeyConstraint(['service_id'], ['Service.id'], 'accesstoken_ibfk_2'),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('MACNonce',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('access_token_id', Identifier(), nullable=True),
        sa.Column('nonce', sa.String(length=30), nullable=True),
        sa.Column('status', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.ForeignKeyConstraint(['access_token_id'], ['AccessToken.id'], 'macnonce_ibfk_1'),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('OperatorAuth',
        sa.Column('operator_id', Identifier(), nullable=False),
        sa.Column('login_id', sa.String(length=32), nullable=True),
        sa.Column('password', sa.String(length=32), nullable=True),
        sa.Column('auth_code', sa.String(length=32), nullable=True),
        sa.Column('access_token', sa.String(length=32), nullable=True),
        sa.Column('secret_key', sa.String(length=32), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.ForeignKeyConstraint(['operator_id'], ['Operator.id'], 'operatorauth_ibfk_1'),
        sa.PrimaryKeyConstraint('operator_id'),
        sa.UniqueConstraint('login_id')
        )

def create_audit_related_tables():
    op.create_table('OperatorActionHistory',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('operator_id', Identifier(), nullable=True),
        sa.Column('function', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['operator_id'], ['Operator.id'], 'operatoractionhistory_ibfk_1'),
        sa.PrimaryKeyConstraint('id')
        )

def create_bookmark_related_tables():
    op.create_table('Bookmark',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('url', sa.String(length=1024), nullable=True),
        sa.Column('organization_id', Identifier(), nullable=True),
        sa.Column('status', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['Organization.id'], 'bookmark_ibfk_1'),
        sa.PrimaryKeyConstraint('id')
        )

def upgrade():
    create_master_tables()
    create_plugin_related_tables()
    create_user_related_tables()
    create_organization_table()
    create_mail_magazine_related_tables()
    create_event_related_tables()
    create_sales_related_tables()
    create_venue_related_tables()
    create_checkout_related_tables()
    create_multicheckout_related_tables()
    create_sej_related_tables()
    create_point_related_tables()
    create_order_related_tables()
    create_cart_related_tables()
    create_auth_related_tables()
    create_audit_related_tables()
    create_bookmark_related_tables()

def downgrade():
    op.drop_table('OrderedProductAttribute')
    op.drop_table('orders_seat')
    op.drop_table('cat_seat')
    op.drop_table('ticketing_cartedproductitems')
    op.drop_table('Seat_SeatAdjacency')
    op.drop_table('OrderedProductItem')
    op.drop_table('ticketing_cartedproducts')
    op.drop_table('VenueArea_group_l0_id')
    op.drop_table('OrderedProduct')
    op.drop_table('SeatIndex')
    op.drop_table('SeatAttribute')
    op.drop_table('SeatStatus')
    op.drop_table('SeatAdjacency')
    op.drop_table('SeatAdjacencySet')
    op.drop_table('SeatIndexType')
    op.drop_table('Order')
    op.drop_table('ticketing_carts')
    op.drop_table('BuyerConditionSet')
    op.drop_table('Seat')
    op.drop_table('ProductItem')
    op.drop_table('StockStatus')
    op.drop_table('PaymentDeliveryMethodPair')
    op.drop_table('Venue')
    op.drop_table('Stock')
    op.drop_table('Product')
    op.drop_table('StockAllocation')
    op.drop_table('StockType')
    op.drop_table('Performance')
    op.drop_table('StockHolder')
    op.drop_table('SalesSegment')
    op.drop_table('MACNonce')
    op.drop_table('MailSubscription')
    op.drop_table('OperatorRole_Operator')
    op.drop_table('Event')
    op.drop_table('OperatorAuth')
    op.drop_table('AccessToken')
    op.drop_table('OperatorActionHistory')
    op.drop_table('MailMagazine')
    op.drop_table('DeliveryMethod')
    op.drop_table('Bookmark')
    op.drop_table('UserPointHistory')
    op.drop_table('Operator')
    op.drop_table('PaymentMethod')
    op.drop_table('Account')
    op.drop_table('UserCredential')
    op.drop_table('UserProfile')
    op.drop_table('ShippingAddress')
    op.drop_table('Organization')
    op.drop_table('UserPointAccount')
    op.drop_table('User')
    op.drop_table('CheckoutItem')
    op.drop_table('Permission')
    op.drop_table('BuyerCondition')
    op.drop_table('BankAccount')
    op.drop_table('multicheckout_inquiry_response_card_history')
    op.drop_table('SejTicket')
    op.drop_table('SejRefundTicket')
    op.drop_table('PaymentMethodPlugin')
    op.drop_table('secure3d_req_enrol_request')
    op.drop_table('Bank')
    op.drop_table('SejRefundEvent')
    op.drop_table('SejNotification')
    op.drop_table('Service')
    op.drop_table('multicheckout_inquiry_response_card')
    op.drop_table('payment_reserved_number')
    op.drop_table('ticketstar_playguide.User')
    op.drop_table('MemberShip')
    op.drop_table('Checkout')
    op.drop_table('secure3d_req_auth_response')
    op.drop_table('DeliveryMethodPlugin')
    op.drop_table('multicheckout_response_card')
    op.drop_table('SejTicketTemplateFile')
    op.drop_table('Site')
    op.drop_table('ticketstar_playguide.Order')
    op.drop_table('SejOrder')
    op.drop_table('secure3d_req_auth_request')
    op.drop_table('PostCode')
    op.drop_table('SejFile')
    op.drop_table('secure3d_req_enrol_response')
    op.drop_table('multicheckout_request_card')
    op.drop_table('VenueArea')
    op.drop_table('reserved_number')
    op.drop_table('OperatorRole')
    ### end Alembic commands ###
