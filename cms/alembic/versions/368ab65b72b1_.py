"""empty message

Revision ID: 368ab65b72b1
Revises: 3f53c33dd49c
Create Date: 2012-05-06 20:17:40.712071

"""

# revision identifiers, used by Alembic.
revision = '368ab65b72b1'
down_revision = '3f53c33dd49c'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

##:IMPORT_SYMBOL
import pkg_resources
def import_symbol(symbol):
    return pkg_resources.EntryPoint.parse("x=%s" % symbol).load(False)


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('role_permissions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.Enum(*import_symbol("altaircms.auth.models:PERMISSIONS")), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.CheckConstraint('TODO'),
    sa.ForeignKeyConstraint(['role_id'], ['role.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table(u'role2permission')
    op.drop_table(u'permission')
    ### end Alembic commands ###

def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table(u'permission',
    sa.Column(u'id', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column(u'name', mysql.VARCHAR(length=255), nullable=True),
    sa.PrimaryKeyConstraint(u'id')
    )
    op.create_table(u'role2permission',
    sa.Column(u'id', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column(u'role_id', mysql.INTEGER(display_width=11), nullable=True),
    sa.Column(u'permission_id', mysql.INTEGER(display_width=11), nullable=True),
    sa.ForeignKeyConstraint(['permission_id'], [u'permission.id'], name=u'role2permission_ibfk_1'),
    sa.ForeignKeyConstraint(['role_id'], [u'role.id'], name=u'role2permission_ibfk_2'),
    sa.PrimaryKeyConstraint(u'id')
    )
    op.drop_table('role_permissions')
    ### end Alembic commands ###
