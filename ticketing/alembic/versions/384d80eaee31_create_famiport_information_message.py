# -*- coding: utf-8 -*-
"""create famiport_information_message

Revision ID: 384d80eaee31
Revises: 12333853df26
Create Date: 2015-05-01 15:25:10.577029

"""

# revision identifiers, used by Alembic.
revision = '384d80eaee31'
down_revision = '12333853df26'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf
from altair.app.ticketing.famiport.utils import InformationResultCodeEnum

Identifier = sa.BigInteger


def upgrade():
    op.create_table(
        'FamiPortInformationMessage',
        sa.Column('id', Identifier),
        sa.Column('result_code', sa.Enum('WithInformation', 'ServiceUnavailable'), unique=True, nullable=False),  # 案内処理結果コード名
        sa.Column('message', sa.Unicode(1000), nullable=False),  # 案内文言
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sqlf.current_timestamp()),
        sa.Column('updated_at', sa.TIMESTAMP, nullable=False, server_default=text('0')),
        sa.PrimaryKeyConstraint('id')
        )

def downgrade():
    op.drop_table('FamiPortInformationMessage')
