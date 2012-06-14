"""add column for ticketlist

Revision ID: 195157f232b3
Revises: 22b3e2ae4c34
Create Date: 2012-06-14 13:28:27.576483

"""

# revision identifiers, used by Alembic.
revision = '195157f232b3'
down_revision = '22b3e2ae4c34'

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('widget_ticketlist', sa.Column('caption', sa.UnicodeText(), nullable=True))
    op.add_column('widget_ticketlist', sa.Column('target_performance_id', sa.Integer(), sa.ForeignKey("performance.id", use_alter=True, name="widget_ticket_list_target_performance_id_performance_id_fk"), nullable=True))
    op.execute("alter table widget_ticketlist add constraint widget_ticket_list_target_performance_id_performance_id_fk foreign key (target_performance_id) references performance(id);")

def downgrade():
    op.execute("alter table widget_ticketlist drop foreign key widget_ticket_list_target_performance_id_performance_id_fk;")
    op.drop_column('widget_ticketlist', 'target_performance_id')
    op.drop_column('widget_ticketlist', 'caption')

