"""change for ticketlist widget

Revision ID: 3ccdbfde6dfe
Revises: 42b374fa3b57
Create Date: 2013-02-21 12:02:27.307721

"""

# revision identifiers, used by Alembic.
revision = '3ccdbfde6dfe'
down_revision = '42b374fa3b57'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    op.drop_column('widget_ticketlist', u'kind')
    op.add_column('widget_ticketlist', sa.Column('target_salessegment_id', sa.Integer(), nullable=True))
    op.create_foreign_key("widget_ticket_list_target_sale_id_sale_id_fk", "widget_ticketlist", "sale", ["target_salessegment_id"], ["id"])
    op.add_column('widget_ticketlist', sa.Column('display_type', sa.Unicode(length=255), nullable=True))

def downgrade():
    op.drop_constraint("widget_ticket_list_target_sale_id_sale_id_fk", "widget_ticketlist", type="foreignkey")
    op.drop_index("widget_ticket_list_target_sale_id_sale_id_fk", "widget_ticketlist")
    op.drop_column('widget_ticketlist', 'target_salessegment_id')
    op.drop_column('widget_ticketlist', 'display_type')
    op.add_column('widget_ticketlist', sa.Column(u'kind', mysql.VARCHAR(length=255), nullable=True))
