"""add_auth_identifier_and_auth_secret_to_member

Revision ID: 4bd8fee92199
Revises: 313b31142eb7
Create Date: 2015-10-06 09:46:47.077791

"""

# revision identifiers, used by Alembic.
revision = '4bd8fee92199'
down_revision = '313b31142eb7'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    #with op.batch_alter_table('Member') as bop:
    #    bop.drop_constraint('Member_ibfk_2', type_='foreign_key')
    #    bop.alter_column('user_id', existing_type=Identifier(), nullable=True)
    #    bop.add_column(sa.Column('auth_identifier', sa.Unicode(64)))
    #    bop.add_column(sa.Column('auth_secret', sa.Unicode(64)))
    #    bop.add_column(sa.Column('membership_id', Identifier())
    #    bop.create_index('auth_identifier', ['auth_identifier'])
    op.execute('ALTER TABLE Member DROP FOREIGN KEY Member_ibfk_2, MODIFY COLUMN user_id BIGINT NULL, ADD COLUMN auth_identifier VARCHAR(64) NULL, ADD COLUMN auth_secret VARCHAR(64) NULL, ADD COLUMN membership_id BIGINT, ADD INDEX auth_identifier (auth_identifier);')
    op.execute('UPDATE Member JOIN MemberGroup ON Member.membergroup_id=MemberGroup.id LEFT JOIN UserCredential ON Member.user_id=UserCredential.user_id AND MemberGroup.membership_id=UserCredential.membership_id SET Member.auth_identifier=UserCredential.auth_identifier, Member.auth_secret=UserCredential.auth_secret, Member.membership_id=MemberGroup.membership_id WHERE Member.deleted_at IS NULL AND UserCredential.deleted_at IS NOT NULL;')
    op.alter_column('Member', 'membership_id', existing_type=Identifier(), nullable=False)
    op.create_foreign_key('Member_ibfk_3', 'Member', 'Membership', ['membership_id'], ['id'], ondelete='cascade')

def downgrade():
    op.execute('UPDATE Member JOIN MemberGroup ON Member.membergroup_id=MemberGroup.id JOIN UserCredential ON Member.user_id=UserCredential.user_id AND MemberGroup.membership_id=UserCredential.membership_id SET UserCredential.auth_identifier=Member.auth_identifier, UserCredential.auth_secret=Member.auth_secret WHERE Member.deleted_at IS NULL AND UserCredential.deleted_at IS NOT NULL;')
    op.execute('ALTER TABLE Member DROP FOREIGN KEY Member_ibfk_3, DROP COLUMN auth_identifier, DROP COLUMN auth_secret, DROP COLUMN membership_id, MODIFY COLUMN user_id BIGINT NOT NULL, ADD CONSTRAINT Member_ibfk_2 FOREIGN KEY Member_ibfk_2 (user_id) REFERENCES User (id);');
    # with op.batch_alter_table('Member') as bop:
    #     bop.alter_column('user_id', existing_type=Identifier(), nullable=False)
    #     bop.drop_constraint('Member_ibfk_3', type_='foreignkey')
    #     bop.drop_column('auth_identifier')
    #     bop.drop_column('auth_secret')
    #     bop.drop_column('membership_id')
