"""change foreignkey constraint

Revision ID: ebba25add85
Revises: 7ba28a5f066
Create Date: 2016-09-09 17:28:19.548066

"""

# revision identifiers, used by Alembic.
revision = 'ebba25add85'
down_revision = '7ba28a5f066'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.drop_constraint('Organization_ibfk_1', 'Organization', type_='foreignkey')
    op.create_foreign_key(
        'Organization_ibfk_1', 'Organization', 'Host', ['canonical_host_name'], ['host_name'], onupdate='CASCADE'
    )

def downgrade():
    op.drop_constraint('Organization_ibfk_1', 'Organization', type_='foreignkey')
    op.create_foreign_key(
        'Organization_ibfk_1', 'Organization', 'Host', ['canonical_host_name'], ['host_name']
    )
