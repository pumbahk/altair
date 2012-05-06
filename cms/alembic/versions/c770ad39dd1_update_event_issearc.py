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
    # op.alter_column("event",
    #                 "issearchable", type_=sa.Boolean, existing_type=sa.Integer)

    op.add_column("event", sa.Column("issearchable", sa.Boolean))

def downgrade():
    # op.alter_column("event",
    #                 "issearchable", type_=sa.Integer, existing_type=sa.Boolean)
    op.drop_column("event", "issearchable")

