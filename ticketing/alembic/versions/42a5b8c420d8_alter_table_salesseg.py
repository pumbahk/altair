"""alter table SalesSegmentGroup add column

Revision ID: 42a5b8c420d8
Revises: 2e752dabe105
Create Date: 2013-03-28 10:50:36.155552

"""

# revision identifiers, used by Alembic.
revision = '42a5b8c420d8'
down_revision = '2e752dabe105'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column(u'SalesSegmentGroup', sa.Column('account_id', Identifier(), nullable=True))
    op.create_foreign_key(
        name='SalesSegmentGroup_ibfk_2',
        source='SalesSegmentGroup',
        referent='Account',
        local_cols=['account_id'],
        remote_cols=['id'],
        )
    op.add_column(u'SalesSegment', sa.Column('account_id', Identifier(), nullable=True))
    op.create_foreign_key(
        name='SalesSegment_ibfk_3',
        source='SalesSegment',
        referent='Account',
        local_cols=['account_id'],
        remote_cols=['id'],
        )
    op.execute("update SalesSegmentGroup ssg, Event e set ssg.account_id = e.account_id")
    op.execute("update SalesSegment ss, Performance p, Event e set ss.account_id = e.account_id where ss.performance_id = p.id and p.event_id = e.id")

def downgrade():
    op.drop_constraint('SalesSegment_ibfk_3', u'SalesSegment', type='foreignkey')
    op.drop_column(u'SalesSegment', 'account_id')
    op.drop_constraint('SalesSegmentGroup_ibfk_2', u'SalesSegmentGroup', type='foreignkey')
    op.drop_column(u'SalesSegmentGroup', 'account_id')

