"""PerformanceSetting.xxx -> Performance.xxx

Revision ID: 30449e9b3ea9
Revises: 1d67a6111a7
Create Date: 2013-10-04 15:57:41.479482

"""

# revision identifiers, used by Alembic.
revision = '30449e9b3ea9'
down_revision = '1d67a6111a7'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger
from sqlalchemy.dialects import mysql

def upgrade():
    op.add_column('Performance', sa.Column('abbreviated_title', sa.Unicode(length=255), nullable=True))
    op.add_column('Performance', sa.Column('note', sa.UnicodeText(), nullable=True))
    op.add_column('Performance', sa.Column('subtitle', sa.Unicode(length=255), nullable=True))
    
    op.execute("""
update Performance as p join PerformanceSetting as ps on p.id = ps.performance_id set p.note = ps.note,  p.subtitle = ps.subtitle,  p.abbreviated_title = ps.abbreviated_title;
""")

    op.drop_column('PerformanceSetting', u'note')
    op.drop_column('PerformanceSetting', u'subtitle')
    op.drop_column('PerformanceSetting', u'abbreviated_title')

def downgrade():
    op.add_column('PerformanceSetting', sa.Column(u'abbreviated_title', mysql.VARCHAR(length=255), nullable=True))
    op.add_column('PerformanceSetting', sa.Column(u'subtitle', mysql.VARCHAR(length=255), nullable=True))
    op.add_column('PerformanceSetting', sa.Column(u'note', mysql.TEXT(), nullable=True))

    op.execute("""
update Performance as p join PerformanceSetting as ps on p.id = ps.performance_id set ps.note = p.note,  ps.subtitle = p.subtitle,  ps.abbreviated_title = p.abbreviated_title;
""")

    op.drop_column('Performance', 'subtitle')
    op.drop_column('Performance', 'note')
    op.drop_column('Performance', 'abbreviated_title')
