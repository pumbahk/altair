"""add_request_id_to_multicheckout_response_card

Revision ID: 15f7cc655ec3
Revises: 43d4315d85f4
Create Date: 2014-02-28 17:30:25.879566

"""

# revision identifiers, used by Alembic.
revision = '15f7cc655ec3'
down_revision = '43d4315d85f4'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('multicheckout_response_card', sa.Column('request_id', Identifier(), nullable=True))
    op.create_foreign_key('multicheckout_response_card_ibfk_1', 'multicheckout_response_card', 'multicheckout_request_card', ['request_id'], ['id'])

def downgrade():
    op.drop_constraint('multicheckout_response_card_ibfk_1', 'multicheckout_response_card', type='foreignkey')
    op.drop_column('multicheckout_response_card', 'request_id')
