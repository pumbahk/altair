# -*- coding: utf-8 -*-
"""add_rendered_template_columns_on_organization_setting

Revision ID: 4dee681121d2
Revises: 2a5de84a8bb0
Create Date: 2018-08-01 19:34:58.537347

"""

# revision identifiers, used by Alembic.
revision = '4dee681121d2'
down_revision = '2a5de84a8bb0'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    # テンプレートや静的コンテンツを優先して参照するORGディレクトリ
    op.add_column('OrganizationSetting',
                  sa.Column('rendered_template_1', sa.String(length=32), nullable=False, server_default='-'))
    # rendered_template_1に該当のファイルがなかった場合に参照するORGディレクトリ
    op.add_column('OrganizationSetting',
                  sa.Column('rendered_template_2', sa.String(length=32), nullable=False, server_default='-'))

    # 初期設定: rendered_template_1は各自のORGのショートネームを、rendered_template_2は「使用しない」を表す「-」を登録
    op.execute('''
        UPDATE
            `OrganizationSetting` AS os,
            `Organization` AS o
        SET
            os.rendered_template_1 = o.short_name,
            os.rendered_template_2 = '-'
        WHERE
            os.organization_id = o.id;
    ''')

    # すでに__base__ディレクトリへの参照を開始しているORGを登録
    op.execute('''
        UPDATE
            `OrganizationSetting` AS os
        SET
            os.rendered_template_2 = '__base__'
        WHERE
            os.rendered_template_1 IN (
                'AF',
                'AR',
                'BW',
                'DT',
                'GP',
                'HM',
                'JJ',
                'KB',
                'KF',
                'KJ',
                'MH',
                'MX',
                'PC',
                'PH',
                'SQ',
                'WP',
                'JH'
            );
    ''')


def downgrade():
    op.drop_column('OrganizationSetting', 'rendered_template_1')
    op.drop_column('OrganizationSetting', 'rendered_template_2')
