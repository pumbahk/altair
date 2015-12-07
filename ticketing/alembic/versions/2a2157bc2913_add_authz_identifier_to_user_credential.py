"""add_authz_identifier_to_user_credential

Revision ID: 2a2157bc2913
Revises: 4bd8fee92199
Create Date: 2015-10-07 02:10:28.708808

"""

# revision identifiers, used by Alembic.
revision = '2a2157bc2913'
down_revision = '4bd8fee92199'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    # with op.batch_alter_table('UserCredential') as bop:
    #     bop.add_column(sa.Column('authz_identifier', sa.Unicode(96), nullable=True))
    #     bop.alter_column('auth_identifier', type_=sa.Unicode(128), existing_nullable=True)
    op.execute('ALTER TABLE UserCredential MODIFY COLUMN auth_identifier VARCHAR(128) NULL, ADD COLUMN authz_identifier VARCHAR(96) NULL;')
def downgrade():
    # with op.batch_alter_table('UserCredential') as bop:
    #     bop.drop_column('authz_identifier')
    #     bop.alter_column('auth_identifier', type_=sa.Unicode(255), existing_nullable=True)
    op.execute('ALTER TABLE UserCredential MODIFY COLUMN auth_identifier VARCHAR(255) NULL, DROP COLUMN authz_identifier;')
