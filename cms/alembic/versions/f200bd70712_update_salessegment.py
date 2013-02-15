"""update salessegment

Revision ID: f200bd70712
Revises: 52b486f28c3f
Create Date: 2013-02-14 18:34:09.006337

"""

# revision identifiers, used by Alembic.
revision = 'f200bd70712'
down_revision = '52b486f28c3f'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    op.create_table('salessegment_group',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('event_id', sa.Integer(), nullable=True),
                    sa.Column('name', sa.Unicode(length=255), nullable=True),
                    sa.Column('kind', sa.Unicode(length=255), nullable=True),
                    sa.ForeignKeyConstraint(['event_id'], ['event.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.add_column(u'sale', sa.Column('performance_id', sa.Integer(), nullable=True))
    op.create_foreign_key(u"fk_sale_performance_id_to_performance_id","sale", "performance", ["performance_id"], ["id"])
    op.add_column(u'sale', sa.Column('group_id', sa.Integer(), nullable=True))
    op.create_foreign_key(u"sale_ibfk_2", "sale", "salessegment_group", ["group_id"], ["id"])
    op.drop_constraint("fk_sale_event_id_to_event_id", "sale", type="foreignkey")
    op.drop_column(u'sale', u'event_id')
    op.drop_column(u'sale', u'kind')
    op.drop_column(u'sale', u'name')
    op.drop_table(u'performance_ticket')

def downgrade():
    op.add_column(u'sale', sa.Column(u'name',  mysql.VARCHAR(length=255), nullable=True))
    op.add_column(u'sale', sa.Column(u'kind', mysql.VARCHAR(length=255), nullable=True))
    op.add_column(u'sale', sa.Column(u'event_id', mysql.INTEGER(display_width=11), nullable=True))
    op.create_foreign_key(u"fk_sale_event_id_to_event_id","sale", "event", ["event_id"], ["id"])
    op.drop_constraint("sale_ibfk_2", "sale", type="foreignkey")
    op.drop_column(u'sale', 'group_id')
    op.drop_constraint("fk_sale_performance_id_to_performance_id", "sale", type="foreignkey")
    op.drop_column(u'sale', 'performance_id')
    op.drop_table('salessegment_group')
    op.create_table(u'performance_ticket',
                    sa.Column(u'performance_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
                    sa.Column(u'ticket_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
                    sa.ForeignKeyConstraint(['performance_id'], [u'performance.id'], name=u'fk_performance_ticket_performance_id_to_performance_id'),
                    sa.ForeignKeyConstraint(['ticket_id'], [u'ticket.id'], name=u'fk_performance_ticket_ticket_id_to_ticket_id'),
                    sa.PrimaryKeyConstraint()
                    )
