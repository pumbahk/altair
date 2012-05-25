"""create purchase widget

Revision ID: 1ba3266beb3
Revises: 3ba63bddcaff
Create Date: 2012-05-25 13:31:33.298052

"""

# revision identifiers, used by Alembic.
revision = '1ba3266beb3'
down_revision = '3ba63bddcaff'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    op.create_table(u'widget_purchase',
                    sa.Column(u'id', sa.Integer(display_width=11), nullable=False),
                    sa.Column(u'external_link', sa.Unicode(length=255), nullable=True),
                    sa.Column(u'kind', sa.Unicode(length=32), nullable=False),
                    sa.ForeignKeyConstraint(['id'], [u'widget.id'], name=u'fk_widget_purchase_id'),
                    sa.PrimaryKeyConstraint(u'id')
                    )
   
def downgrade():
    op.execute("ALTER TABLE widget_purchase DROP FOREIGN KEY fk_widget_purchase_id")
    op.drop_table("widget_purchase")

