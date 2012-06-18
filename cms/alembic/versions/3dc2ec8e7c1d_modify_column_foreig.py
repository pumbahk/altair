"""modify column foreign key

Revision ID: 3dc2ec8e7c1d
Revises: 1faa6cd3ba1
Create Date: 2012-06-18 16:48:23.162965

"""

# revision identifiers, used by Alembic.
revision = '3dc2ec8e7c1d'
down_revision = '1faa6cd3ba1'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute("alter table ticket drop foreign key fk_ticket_sale_id_to_sale_id;")
    op.execute("alter table ticket add constraint fk_ticket_sale_id_to_sale_id FOREIGN KEY (sale_id) REFERENCES sale (id) ON DELETE CASCADE;")
    op.execute("alter table sale drop foreign key fk_sale_performance_id_to_performance_id;")
    op.execute("alter table sale add constraint fk_sale_performance_id_to_performance_id FOREIGN KEY (performance_id) REFERENCES performance (id) ON DELETE CASCADE;")

def downgrade():
    op.execute("alter table ticket drop foreign key fk_ticket_sale_id_to_sale_id;")
    op.execute("alter table ticket add constraint fk_ticket_sale_id_to_sale_id FOREIGN KEY (sale_id) REFERENCES sale (id);")
    op.execute("alter table sale drop foreign key fk_sale_performance_id_to_performance_id;")
    op.execute("alter table sale add constraint fk_sale_performance_id_to_performance_id FOREIGN KEY (performance_id) REFERENCES performance (id);")
