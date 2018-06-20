# -*- coding:utf-8 -*-

"""add_foreign_key_on_augus_performance

Revision ID: 3bb9b6990f58
Revises: 1451c64d8a4c
Create Date: 2018-06-19 14:33:30.244606

"""

# revision identifiers, used by Alembic.
revision = '3bb9b6990f58'
down_revision = '1451c64d8a4c'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    # Performance.id（DEFAULT NOT NULL）とAugusPerformance.performance_id（DEFAULT NULL）の違いがあるため、外部キーで繋げない。
    # また、未来日にもAugusPerformance.performance_idがNULLのレコードが存在している
    # op.create_foreign_key(
    #     name='AugusPerformance_ibfk_1',
    #     source='AugusPerformance',
    #     referent='Perforance',
    #     local_cols=['performance_id'],
    #     remote_cols=['id'],
    #     onupdate='CASCADE',
    #     ondelete='CASCADE'
    # )

    op.create_foreign_key(
        name='AugusPerformance_ibfk_1',
        source='AugusPerformance',
        referent='AugusAccount',
        local_cols=['augus_account_id'],
        remote_cols=['id'],
        onupdate='CASCADE',
        ondelete='CASCADE'
    )


def downgrade():
    op.drop_constraint('AugusPerformance_ibfk_1', 'AugusPerformance', type_='foreignkey')
    op.drop_index('AugusPerformance_ibfk_1', 'AugusPerformance')
