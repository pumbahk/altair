"""add_column Refund.order_count, status

Revision ID: 3f01910d65e7
Revises: 10860fae231f
Create Date: 2014-05-21 13:52:58.822491

"""

# revision identifiers, used by Alembic.
revision = '3f01910d65e7'
down_revision = '10860fae231f'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table(u'Refund_Performance',
        sa.Column('refund_id', Identifier(), nullable=False),
        sa.Column('performance_id', Identifier(), nullable=False),
        sa.ForeignKeyConstraint(['refund_id'], ['Refund.id'], 'Refund_Performance_ibfk_1', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['performance_id'], ['Performance.id'], 'Refund_Performance_ibfk_2', ondelete='CASCADE')
        )
    op.execute('''
               INSERT INTO Refund_Performance (refund_id, performance_id)
               SELECT DISTINCT `Refund`.id, `Order`.performance_id FROM `Refund`, `Order` WHERE `Refund`.id = `Order`.refund_id AND `Order`.deleted_at IS NULL
               ''')

    op.add_column(u'Refund', sa.Column(u'order_count', sa.Integer, nullable=True))
    op.execute('''
               UPDATE `Refund` SET `Refund`.order_count = 
               (SELECT COUNT(DISTINCT `Order`.id) FROM `Order` WHERE `Refund`.id = `Order`.refund_id AND `Order`.deleted_at IS NULL)
               ''')

    op.add_column(u'Refund', sa.Column(u'status', sa.Integer, nullable=False, default=0, server_default='0'))
    op.execute('''
               UPDATE `Refund`,
               (SELECT COUNT(DISTINCT `Order`.id) AS count, `Order`.refund_id
                FROM `Order`
                WHERE `Order`.refund_id IS NOT NULL AND `Order`.refunded_at IS NOT NULL AND `Order`.deleted_at IS NULL
                GROUP BY `Order`.refund_id) O
               SET `Refund`.status = IF(`Refund`.order_count = O.count, 2, IF(O.count > 0, 1, 0))
               WHERE `Refund`.id = O.refund_id
               ''')

def downgrade():
    op.drop_table(u'Refund_Performance')
    op.drop_column(u'Refund', u'status')
    op.drop_column(u'Refund', u'order_count')
