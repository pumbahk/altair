"""drop useless model

Revision ID: 1f10bad1f8d3
Revises: 420715e73045
Create Date: 2012-07-03 12:26:33.442185

"""

# revision identifiers, used by Alembic.
revision = '1f10bad1f8d3'
down_revision = '420715e73045'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    op.execute('ALTER TABLE site DROP FOREIGN KEY fk_site_client_id_to_client_id;')
    op.execute('ALTER TABLE event DROP FOREIGN KEY fk_event_client_id_to_client_id;')
    op.execute('ALTER TABLE performance DROP FOREIGN KEY fk_performance_client_id_to_client_id;')
    op.execute('ALTER TABLE user DROP FOREIGN KEY fk_user_site_id_to_site_id;')
    op.execute('ALTER TABLE operator DROP FOREIGN KEY fk_operator_client_id_to_client_id;')
    op.execute('ALTER TABLE apikey DROP FOREIGN KEY fk_apikey_client_id_to_client_id;')
    op.execute('ALTER TABLE category DROP FOREIGN KEY fk_category_site_id_to_site_id;')
    op.execute('ALTER TABLE hotword DROP FOREIGN KEY fk_hotword_site_id_to_site_id;')
    op.execute('ALTER TABLE layout DROP FOREIGN KEY fk_layout_site_id_to_site_id;')
    op.execute('ALTER TABLE layout DROP FOREIGN KEY fk_layout_client_id_to_client_id;')
    op.execute('ALTER TABLE page DROP FOREIGN KEY fk_page_site_id_to_site_id;')
    op.execute('ALTER TABLE promotion DROP FOREIGN KEY fk_promotion_site_id_to_site_id;')
    op.execute('ALTER TABLE topcontent DROP FOREIGN KEY fk_topcontent_site_id_to_site_id;')
    op.execute('ALTER TABLE topcontent DROP FOREIGN KEY fk_topcontent_client_id_to_client_id;')
    op.execute('ALTER TABLE topic DROP FOREIGN KEY fk_topic_site_id_to_site_id;')
    op.execute('ALTER TABLE topic DROP FOREIGN KEY fk_topic_client_id_to_client_id;')
    op.execute('ALTER TABLE widget DROP FOREIGN KEY fk_widget_site_id_to_site_id;')
    op.execute('ALTER TABLE widgetdisposition DROP FOREIGN KEY fk_widgetdisposition_site_id_to_site_id;')
    op.execute('ALTER TABLE asset DROP FOREIGN KEY asset_ibfk_1;')
    op.drop_table(u'client')
    op.drop_table(u'order_history')
    op.drop_table(u'site')
    op.drop_table(u'user')
    op.drop_column(u"event", u"client_id")
    op.drop_column(u"performance", u"client_id")
    op.drop_column(u'operator', u'client_id')
    op.drop_column('apikey', u'client_id')
    op.drop_column('asset', u'site_id')
    op.drop_column('category', u'site_id')
    op.drop_column('hotword', u'site_id')
    op.drop_column('layout', u'site_id')
    op.drop_column('layout', u'client_id')
    op.drop_column('page', u'site_id')
    op.alter_column('page_accesskeys', u'hashkey', 
               existing_type=mysql.VARCHAR(length=32), 
               nullable=False)
    op.drop_column('promotion', u'site_id')
    op.drop_column('topcontent', u'site_id')
    op.drop_column('topcontent', u'client_id')
    op.drop_column('topic', u'site_id')
    op.drop_column('topic', u'client_id')
    op.drop_column('widget', u'site_id')
    op.drop_column('widgetdisposition', u'site_id')

def downgrade():
    op.create_table('client',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.Column('name', sa.Unicode(length=255), nullable=True),
                    sa.Column('prefecture', sa.Unicode(length=255), nullable=True),
                    sa.Column('address', sa.Unicode(length=255), nullable=True),
                    sa.Column('email', sa.String(length=255), nullable=True),
                    sa.Column('contract_status', sa.Integer(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('order_history',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.Column('ticket_id', sa.Integer(), nullable=True),
                    sa.Column('user_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['ticket_id'], ['ticket.id'], name="order_history_ticket_id_to_ticket_id"),
                    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name="order_history_user_id_to_user_id"),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('site',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.Column('name', sa.Unicode(length=255), nullable=True),
                    sa.Column('description', sa.Unicode(length=255), nullable=True),
                    sa.Column('url', sa.String(length=255), nullable=True),
                    sa.Column('client_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['client_id'], ['client.id'], name="fk_site_client_id_to_client_id"),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('user',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.Column('email', sa.String(length=255), nullable=True),
                    sa.Column('site_id', sa.Integer(), nullable=True),
                    sa.Column('is_active', sa.Integer(), nullable=True),
                    sa.Column('is_administrator', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['site_id'], ['site.id'], name="fk_user_site_id_to_site_id"),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.add_column(u'operator', sa.Column(u'client_id', mysql.INTEGER(display_width=11), nullable=True))
    op.add_column('apikey', sa.Column(u'client_id', mysql.INTEGER(display_width=11), nullable=True))
    op.add_column('asset', sa.Column(u'site_id', mysql.INTEGER(display_width=11), nullable=True))
    op.add_column('category', sa.Column(u'site_id', mysql.INTEGER(display_width=11), nullable=True))
    op.add_column('hotword', sa.Column(u'site_id', mysql.INTEGER(display_width=11), nullable=True))
    op.add_column('layout', sa.Column(u'site_id', mysql.INTEGER(display_width=11), nullable=True))
    op.add_column('layout', sa.Column(u'client_id', mysql.INTEGER(display_width=11), nullable=True))
    op.add_column('page', sa.Column(u'site_id', mysql.INTEGER(display_width=11), nullable=True))
    op.alter_column('page_accesskeys', u'hashkey', 
               existing_type=mysql.VARCHAR(length=32), 
               nullable=True)
    op.add_column('promotion', sa.Column(u'site_id', mysql.INTEGER(display_width=11), nullable=True))
    op.add_column('topcontent', sa.Column(u'site_id', mysql.INTEGER(display_width=11), nullable=True))
    op.add_column('topcontent', sa.Column(u'client_id', mysql.INTEGER(display_width=11), nullable=True))
    op.add_column('topic', sa.Column(u'site_id', mysql.INTEGER(display_width=11), nullable=True))
    op.add_column('topic', sa.Column(u'client_id', mysql.INTEGER(display_width=11), nullable=True))
    op.add_column('widget', sa.Column(u'site_id', mysql.INTEGER(display_width=11), nullable=True))
    op.add_column('widgetdisposition', sa.Column(u'site_id', mysql.INTEGER(display_width=11), nullable=True))
    op.add_column('event', sa.Column(u'client_id', mysql.INTEGER(display_width=11), nullable=True))
    op.add_column('performance', sa.Column(u'client_id', mysql.INTEGER(display_width=11), nullable=True))
