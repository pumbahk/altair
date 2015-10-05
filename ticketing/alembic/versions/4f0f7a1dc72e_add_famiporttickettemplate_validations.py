"""Add FamiPortTicketTemplate validations

Revision ID: 4f0f7a1dc72e
Revises: 7a537ff5e34
Create Date: 2015-10-05 03:26:43.223622

"""

# revision identifiers, used by Alembic.
revision = '4f0f7a1dc72e'
down_revision = '7a537ff5e34'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf
from altair.models import MutationDict, JSONEncodedDict

def upgrade():
    op.add_column('FamiPortTicketTemplate', sa.Column('rules', MutationDict.as_mutable(JSONEncodedDict(16384)).adapt(sa.UnicodeText), nullable=True))

def downgrade():
    op.drop_column('FamiPortTicketTemplate', 'rules')
