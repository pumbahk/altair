"""add_notation_version_to_sej_ticket_template

Revision ID: cba5b2d872c
Revises: 2a47a06a6a4b
Create Date: 2014-07-09 17:50:53.497608

"""

# revision identifiers, used by Alembic.
revision = 'cba5b2d872c'
down_revision = '2a47a06a6a4b'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('SejTicketTemplateFile', sa.Column('notation_version', sa.Integer(), nullable=False))
    op.execute('''UPDATE SejTicketTemplateFile SET notation_version=1 WHERE SejTicketTemplateFile.template_id='TTTS000001';''')

def downgrade():
    op.drop_column('SejTicketTemplate', 'notation_version')
