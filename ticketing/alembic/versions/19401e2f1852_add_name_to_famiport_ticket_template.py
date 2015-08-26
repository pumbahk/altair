"""add_name_to_famiport_ticket_template

Revision ID: 19401e2f1852
Revises: 2dc08c115933
Create Date: 2015-08-24 12:34:57.877468

"""

# revision identifiers, used by Alembic.
revision = '19401e2f1852'
down_revision = '2dc08c115933'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('FamiPortTicketTemplate', sa.Column('organization_id', Identifier, nullable=True))
    op.add_column('FamiPortTicketTemplate', sa.Column('name', sa.Unicode(255), nullable=True))
    op.execute("""UPDATE FamiPortTicketTemplate SET organization_id=34;""")
    op.execute("""UPDATE FamiPortTicketTemplate SET name=template_code;""")
    op.alter_column('FamiPortTicketTemplate', 'organization_id', nullable=False, existing_nullable=True, existing_type=Identifier)
    op.alter_column('FamiPortTicketTemplate', 'name', nullable=False, existing_nullable=True, existing_type=sa.Unicode(255))
    op.create_foreign_key('FamiPortTicketTemplate_ibfk_1', 'FamiPortTicketTemplate', 'Organization', ['organization_id'], ['id'])

def downgrade():
    op.drop_constraint('FamiPortTicketTemplate_ibfk_1', 'FamiPortTicketTemplate', type_='foreignkey')
    op.drop_column('FamiPortTicketTemplate', 'organization_id')
    op.drop_column('FamiPortTicketTemplate', 'name')
