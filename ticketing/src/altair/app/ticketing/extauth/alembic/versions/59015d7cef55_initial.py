"""initial

Revision ID: 59015d7cef55
Revises: None
Create Date: 2015-10-20 10:34:01.314075

"""

# revision identifiers, used by Alembic.
revision = '59015d7cef55'
down_revision = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf
from altair.models import MutableSpaceDelimitedList, SpaceDelimitedList

Identifier = sa.BigInteger


def upgrade():
    op.create_table(
        'Organization',
        sa.Column('id', Identifier, autoincrement=True, primary_key=True, nullable=False),
        sa.Column('short_name', sa.Unicode(32), nullable=False),
        sa.Column('maximum_oauth_scope', MutableSpaceDelimitedList.as_mutable(SpaceDelimitedList(255)), nullable=False, server_default=text(u"'user_info'")),
        sa.Column('maximum_oauth_client_expiration_time', sa.Integer(), nullable=False, server_default=text(u'63072000'))
        )

    op.create_table(
        'Host',
        sa.Column('host_name', sa.Unicode(128), nullable=False),
        sa.Column('organization_id', Identifier, sa.ForeignKey('Organization.id')),
        sa.PrimaryKeyConstraint('host_name', 'organization_id')
        )

    op.create_table(
        'MemberSet',
        sa.Column('id', Identifier, autoincrement=True, primary_key=True, nullable=False),
        sa.Column('organization_id', Identifier, sa.ForeignKey('Organization.id')),
        sa.Column('name', sa.Unicode(32), nullable=False),
        sa.Column('display_name', sa.Unicode(255), nullable=False),
        sa.Column('applicable_subtype', sa.Unicode(32), nullable=True, index=True),
        sa.Column('use_password', sa.Boolean(), nullable=False, server_default=text(u"1")),
        sa.UniqueConstraint('organization_id', 'name')
        )

    op.create_table(
        'Member',
        sa.Column('id', Identifier, autoincrement=True, primary_key=True, nullable=False),
        sa.Column('member_set_id', Identifier, sa.ForeignKey('MemberSet.id')),
        sa.Column('name', sa.Unicode(255), nullable=False),
        sa.Column('auth_identifier', sa.Unicode(128), nullable=False),
        sa.Column('auth_secret', sa.Unicode(128), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default=text(u"1")),
        sa.UniqueConstraint('member_set_id', 'auth_identifier')
        )

    op.create_table(
        'MemberKind',
        sa.Column('id', Identifier, autoincrement=True, primary_key=True, nullable=False),
        sa.Column('member_set_id', Identifier, sa.ForeignKey('MemberSet.id')),
        sa.Column('name', sa.Unicode(32), nullable=False),
        sa.Column('display_name', sa.Unicode(255), nullable=False),
        sa.Column('show_in_landing_page', sa.Boolean(), nullable=False, server_default=text(u"1")),
        sa.Column('enable_guests', sa.Boolean(), nullable=False, server_default=text(u"0")),
        sa.UniqueConstraint('member_set_id', 'name')
        )

    op.create_table(
        'Membership',
        sa.Column('id', Identifier, autoincrement=True, primary_key=True, nullable=False),
        sa.Column('member_id', Identifier(), sa.ForeignKey('Member.id', ondelete='CASCADE'), nullable=False),
        sa.Column('member_kind_id', Identifier(), sa.ForeignKey('MemberKind.id', ondelete='CASCADE'), nullable=False),
        sa.Column('valid_since', sa.DateTime(), nullable=True),
        sa.Column('expire_at', sa.DateTime(), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default=text(u"1"))
        )

    op.create_table(
        'Operator',
        sa.Column('id', Identifier, autoincrement=True, primary_key=True, nullable=False),
        sa.Column('organization_id', Identifier, sa.ForeignKey('Organization.id'), nullable=False),
        sa.Column('auth_identifier', sa.Unicode(128), unique=True, nullable=False),
        sa.Column('auth_secret', sa.Unicode(128), nullable=True),
        sa.Column('role', sa.Unicode(32), nullable=False)
        )

    op.create_table(
        'OAuthClient',
        sa.Column('id', Identifier, autoincrement=True, primary_key=True, nullable=False),
        sa.Column('organization_id', Identifier, sa.ForeignKey('Organization.id')),
        sa.Column('name', sa.Unicode(128), nullable=False, default=u''),
        sa.Column('client_id', sa.Unicode(128), unique=True, nullable=False),
        sa.Column('client_secret', sa.Unicode(128), nullable=False),
        sa.Column('authorized_scope', MutableSpaceDelimitedList.as_mutable(SpaceDelimitedList(255)), nullable=False, default=u''),
        sa.Column('redirect_uri', sa.Unicode(384), nullable=True),
        sa.Column('valid_since', sa.DateTime(), nullable=True),
        sa.Column('expire_at', sa.DateTime(), nullable=True)
        )

def downgrade():
    op.drop_table('OAuthClient')
    op.drop_table('Operator')
    op.drop_table('Membership')
    op.drop_table('MemberKind')
    op.drop_table('Member')
    op.drop_table('MemberSet')
    op.drop_table('Host')
    op.drop_table('Organization')
