"""add_OrderNo_to_secure3d_req_enrol_response_and_secure3d_req_auth_response

Revision ID: 43d4315d85f4
Revises: 3c93bddaec70
Create Date: 2014-02-28 12:10:22.939634

"""

# revision identifiers, used by Alembic.
revision = '43d4315d85f4'
down_revision = '3c93bddaec70'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('secure3d_req_enrol_response', sa.Column('OrderNo', sa.Unicode(32), nullable=True))
    op.add_column('secure3d_req_enrol_response', sa.Column('request_id', Identifier(), nullable=True))
    op.add_column('secure3d_req_auth_response', sa.Column('OrderNo', sa.Unicode(32), nullable=True))
    op.add_column('secure3d_req_auth_response', sa.Column('request_id', Identifier(), nullable=True))
    op.create_foreign_key('secure3d_req_enrol_response_ibfk_1', 'secure3d_req_enrol_response', 'secure3d_req_enrol_request', ['request_id'], ['id'])
    op.create_foreign_key('secure3d_req_auth_response_ibfk_1', 'secure3d_req_auth_response', 'secure3d_req_auth_request', ['request_id'], ['id'])

def downgrade():
    op.drop_constraint('secure3d_req_enrol_response_ibfk_1', 'secure3d_req_enrol_response')
    op.drop_constraint('secure3d_req_auth_response_ibfk_1', 'secure3d_req_auth_response')
    op.drop_column('secure3d_req_auth_response', 'request_id')
    op.drop_column('secure3d_req_auth_response', 'OrderNo')
    op.drop_column('secure3d_req_enrol_response', 'request_id')
    op.drop_column('secure3d_req_enrol_response', 'OrderNo')
