"""create table OperatorRoute

Revision ID: 1569761b748d
Revises: 52e1704387c5
Create Date: 2019-07-22 18:54:08.553652

"""

# revision identifiers, used by Alembic.
revision = '1569761b748d'
down_revision = '52e1704387c5'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table('OperatorGroup',
                    sa.Column('id', Identifier(), nullable=False, autoincrement=True),
                    sa.Column('name', sa.String(length=255), nullable=True),
                    sa.Column('organization_id', Identifier(), nullable=False),
                    sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
                    sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.ForeignKeyConstraint(['organization_id'], ['Organization.id'],
                                            'OperatorGroup_Organization_ibfk_1'),
                    )

    op.create_table('OperatorGroup_Event',
                    sa.Column('operator_group_id', Identifier(), nullable=False),
                    sa.Column('event_id', Identifier(), nullable=False),
                    sa.ForeignKeyConstraint(['event_id'], ['Event.id'], 'OperatorGroup_Event_ibfk_1'),
                    sa.ForeignKeyConstraint(['operator_group_id'], ['OperatorGroup.id'], 'OperatorGroup_Event_ibfk_2'),
                    sa.UniqueConstraint('event_id', name="ix_OperatorGroup_Event_event_id"),
                    sa.PrimaryKeyConstraint('event_id')
                    )

    op.create_table('OperatorRouteGroup',
                    sa.Column('id', Identifier(), nullable=False, autoincrement=True),
                    sa.Column('name', sa.String(length=255), nullable=True),
                    sa.Column('status', sa.Boolean(), nullable=False, server_default='1'),
                    sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
                    sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
                    sa.Column('organization_id', Identifier(), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.ForeignKeyConstraint(['organization_id'], ['Organization.id'],
                                            'OperatorRouteGroup_Organization_ibfk_1'),
                    )

    op.create_table('OperatorRoute',
                    sa.Column('id', Identifier(), nullable=False, autoincrement=True),
                    sa.Column('route_name', sa.String(length=255), nullable=True),
                    sa.Column('operator_route_group_id', Identifier(), nullable=False),
                    sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
                    sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
                    sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    sa.ForeignKeyConstraint(['operator_route_group_id'], ['OperatorRouteGroup.id'],
                                            'OperatorRoute_OperatorRouteGroup_ibfk_1'),
                    )

    op.execute(
        "INSERT INTO Permission (operator_role_id, category_name, permit) VALUES(3, 'mini_admin_viewer', 1)")

    op.add_column(u'Operator', sa.Column(u'operator_group_id', Identifier(),
                                         sa.ForeignKey('OperatorGroup.id', name='Operator_ibfk_2'), nullable=True))

    op.add_column(u'Operator', sa.Column(u'operator_route_group_id', Identifier(),
                                         sa.ForeignKey('OperatorRouteGroup.id', name='Operator_ibfk_3'), nullable=True))


def downgrade():
    op.drop_constraint('Operator_ibfk_3', 'Operator', type='foreignkey')
    op.drop_column(u'Operator', u'operator_route_group_id')

    op.drop_constraint('Operator_ibfk_2', 'Operator', type='foreignkey')
    op.drop_column(u'Operator', u'operator_group_id')

    op.execute(
        "DELETE FROM Permission WHERE operator_role_id=3 AND category_name='mini_admin_viewer' AND permit=1")

    op.drop_table('OperatorRoute')
    op.drop_table('OperatorRouteGroup')
    op.drop_table('OperatorGroup_Event')
    op.drop_table('OperatorGroup')
