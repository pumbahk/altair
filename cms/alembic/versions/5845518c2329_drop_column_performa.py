"""drop column performance_id

Revision ID: 5845518c2329
Revises: 3dc2ec8e7c1d
Create Date: 2012-06-18 19:56:11.335450

"""

# revision identifiers, used by Alembic.
revision = '5845518c2329'
down_revision = '3dc2ec8e7c1d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute("alter table sale drop foreign key fk_sale_performance_id_to_performance_id;")
    op.drop_column('sale', 'performance_id')

def downgrade():
    op.add_column('sale', sa.Column(Integer, ForeignKey('performance.id', ondelete='CASCADE')))
