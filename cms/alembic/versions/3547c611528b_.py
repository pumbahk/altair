"""empty message

Revision ID: 3547c611528b
Revises: 39310a55951f
Create Date: 2012-05-31 11:21:07.282303

"""

# revision identifiers, used by Alembic.
revision = '3547c611528b'
down_revision = '39310a55951f'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    op.create_table('operator_role',
    sa.Column('operator_id', sa.Integer(), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['operator_id'], ['operator.id'], ),
    sa.ForeignKeyConstraint(['role_id'], ['role.id'], ),
    sa.PrimaryKeyConstraint()
    )
    op.execute("ALTER TABLE operator DROP FOREIGN KEY operator_ibfk_2")
    op.drop_column('operator', u'role_id')


def downgrade():
    op.add_column('operator', sa.Column(u'role_id', mysql.INTEGER(display_width=11), nullable=True))
    op.drop_table("operator_role")

