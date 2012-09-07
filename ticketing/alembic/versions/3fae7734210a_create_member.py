"""create_member

Revision ID: 3fae7734210a
Revises: 4725c95a84a0
Create Date: 2012-09-03 15:38:34.016989

"""

# revision identifiers, used by Alembic.
revision = '3fae7734210a'
down_revision = '4725c95a84a0'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf
from sqlalchemy.dialects import mysql

Identifier = sa.BigInteger

def upgrade():
    op.create_table('Member',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('user_id', Identifier(), nullable=False),
        sa.Column('membergroup_id', Identifier(), nullable=False),
        sa.ForeignKeyConstraint(['membergroup_id'], ['MemberGroup.id'], name='Member_ibfk_1'),
        sa.ForeignKeyConstraint(['user_id'], ['User.id'], 'Member_ibfk_2'),
        sa.PrimaryKeyConstraint('id')
        )
    op.execute('INSERT INTO Member (id, user_id, membergroup_id) SELECT id, id, membergroup_id FROM User WHERE membergroup_id IS NOT NULL')
    op.drop_constraint('User_ibfk_3', 'User', type='foreignkey')
    op.drop_column('User', 'membergroup_id')

def downgrade():
    op.add_column(u'User', sa.Column('membergroup_id', Identifier(),
        sa.ForeignKey('MemberGroup.id', name='User_ibfk_3'),
        nullable=True))
    op.execute('UPDATE User, Member SET User.membergroup_id=Member.membergroup_id WHERE User.id=Member.user_id')
    op.drop_constraint('Member_ibfk_1', 'Member', type='foreignkey')
    op.drop_constraint('Member_ibfk_2', 'Member', type='foreignkey')
    op.drop_table('Member')
