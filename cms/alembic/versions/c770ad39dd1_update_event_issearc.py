"""update event.issearchable field

Revision ID: c770ad39dd1
Revises: 1e3174b92c80
Create Date: 2012-05-02 10:23:32.040818

"""

# revision identifiers, used by Alembic.
revision = 'c770ad39dd1'
down_revision = '1e3174b92c80'

from alembic import op
import sqlalchemy as sa


def upgrade():
     op.alter_column("event", 
                     "is_searchable", type_=sa.Boolean, existing_type=sa.Integer,
                     existing_server_default=1)

def downgrade():
     # op.alter_column("event", 
     #                 "is_searchable", type_=sa.Integer, existing_type=sa.Boolean,
     #                 existing_server_default=1)
     pass

