# -*- coding: utf-8 -*-

"""add permission and roles

Revision ID: 14247fb69ba6
Revises: 17534fcc55ec
Create Date: 2017-09-01 17:51:17.639215

"""

# revision identifiers, used by Alembic.
revision = '14247fb69ba6'
down_revision = '17534fcc55ec'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table('Role',
                    sa.Column('id', Identifier(), nullable=False),
                    sa.Column('name', sa.Unicode(length=32), nullable=False),
                    sa.Column('verbose_name', sa.Unicode(length=128), nullable=False),
                    sa.Column('active', sa.Boolean, server_default=('1')),
                    sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
                    sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )

    op.create_table('Permission',
                    sa.Column('id', Identifier(), nullable=False),
                    sa.Column('role_id', Identifier(), nullable=True),
                    sa.Column('category_name', sa.Unicode(length=128), nullable=True),
                    sa.Column('permit', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['role_id'], ['Role.id'], 'Permission_ibfk_1'),
                    sa.PrimaryKeyConstraint('id')
                    )

    op.execute(u"INSERT INTO Role (id, name, verbose_name, active, created_at, updated_at) VALUES (1, 'administrator', '管理者',1, now(), now())")
    op.execute(u"INSERT INTO Role (id, name, verbose_name, active, created_at, updated_at) VALUES (2, 'superoperator', 'スーパーオペレーター',1, now(), now())")
    op.execute(u"INSERT INTO Role (id, name, verbose_name, active, created_at, updated_at) VALUES (3, 'operator', 'オペレーター',1, now(), now())")

    op.execute("INSERT INTO Permission (id, role_id, category_name) VALUES (1, 1, 'administration')")
    op.execute("INSERT INTO Permission (id, role_id, category_name) VALUES (2, 1, 'manage_organization')")
    op.execute("INSERT INTO Permission (id, role_id, category_name) VALUES (3, 1, 'manage_operators')")
    op.execute("INSERT INTO Permission (id, role_id, category_name) VALUES (4, 1, 'manage_service_providers')")
    op.execute("INSERT INTO Permission (id, role_id, category_name) VALUES (5, 1, 'manage_clients')")
    op.execute("INSERT INTO Permission (id, role_id, category_name) VALUES (6, 1, 'manage_member_sets')")
    op.execute("INSERT INTO Permission (id, role_id, category_name) VALUES (7, 1, 'manage_member_kinds')")
    op.execute("INSERT INTO Permission (id, role_id, category_name) VALUES (8, 1, 'manage_members')")

    op.execute("INSERT INTO Permission (id, role_id, category_name) VALUES (9, 2, 'manage_organization')")
    op.execute("INSERT INTO Permission (id, role_id, category_name) VALUES (10, 2, 'manage_operators')")
    op.execute("INSERT INTO Permission (id, role_id, category_name) VALUES (11, 2, 'manage_service_providers')")
    op.execute("INSERT INTO Permission (id, role_id, category_name) VALUES (12, 2, 'manage_clients')")
    op.execute("INSERT INTO Permission (id, role_id, category_name) VALUES (13, 2, 'manage_member_sets')")
    op.execute("INSERT INTO Permission (id, role_id, category_name) VALUES (14, 2, 'manage_member_kinds')")
    op.execute("INSERT INTO Permission (id, role_id, category_name) VALUES (15, 2, 'manage_members')")

    op.execute("INSERT INTO Permission (id, role_id, category_name) VALUES (16, 3, 'manage_member_sets')")
    op.execute("INSERT INTO Permission (id, role_id, category_name) VALUES (17, 3, 'manage_member_kinds')")
    op.execute("INSERT INTO Permission (id, role_id, category_name) VALUES (18, 3, 'manage_members')")

    op.add_column('Operator', sa.Column('role_id', Identifier(), nullable=False, server_default="2"))
    op.execute("ALTER TABLE Operator ADD CONSTRAINT `Operator_ibfk_2` FOREIGN KEY (`role_id`) REFERENCES `Role` (`id`);")
    op.drop_column('Operator', 'role')

    op.add_column('Operator', sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False))
    op.add_column('Operator',sa.Column('updated_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False))

def downgrade():
    op.drop_column('Operator', 'updated_at')
    op.drop_column('Operator', 'created_at')
    op.add_column('Operator', sa.Column('role', sa.Unicode(32), nullable=False, server_default='administrator'))
    op.execute("ALTER TABLE Operator DROP FOREIGN KEY `Operator_ibfk_2`;")
    op.drop_column('Operator', 'role_id')

    op.drop_table('Permission')
    op.drop_table('Role')
