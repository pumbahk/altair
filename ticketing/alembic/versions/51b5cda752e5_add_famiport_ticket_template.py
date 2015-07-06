# encoding: utf-8
"""add_famiport_ticket_template

Revision ID: 51b5cda752e5
Revises: 4ab26bf2ebf2
Create Date: 2015-07-01 18:08:04.023308

"""

# revision identifiers, used by Alembic.
revision = '51b5cda752e5'
down_revision = '4ab26bf2ebf2'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf
from altair.models import MutationDict, JSONEncodedDict

Identifier = sa.BigInteger


def upgrade():
    op.create_table(
        'FamiPortTicketTemplate',
        sa.Column('id', Identifier(), nullable=False, autoincrement=True, primary_key=True),
        sa.Column('template_code', sa.Unicode(13), nullable=False),
        sa.Column('logically_subticket', sa.Boolean(), nullable=False, server_default=text(u"FALSE")),
        sa.Column('mappings', MutationDict.as_mutable(JSONEncodedDict(16384)).adapt(sa.UnicodeText), nullable=False)
        )
    op.execute(u'''INSERT INTO FamiPortTicketTemplate (template_code, logically_subticket, mappings) VALUES ('TTTSTR0001', FALSE, '[["TitleOver", "{{{イベント名}}}"], ["TitleMain", "{{{パフォーマンス名}}}"], ["TitleSub", "{{{公演名副題}}}"], ["FreeSpace1", ""], ["FreeSpace2", ""], ["Date", "{{{開催日}}}"], ["OpenTime", "{{{開場時刻}}}"], ["StartTime", "{{{開始時刻}}}"], ["Price", "{{{チケット価格}}}"], ["Hall", "{{{会場名}}}"], ["Note1", "{{{aux.注意事項1}}}"], ["Note2", "{{{aux.注意事項2}}}"], ["Note3", "{{{aux.注意事項3}}}"], ["Note4", "{{{aux.注意事項4}}}"], ["Note5", "{{{aux.注意事項5}}}"], ["Note6", "{{{aux.注意事項6}}}"], ["Note7", "{{{aux.注意事項7}}}"], ["Seat1", "{{{券種名}}}"], ["Seat2", ""], ["Seat3", ""], ["Seat4", ""], ["Seat5", ""], ["Sub-Title1", "{{{イベント名}}}"], ["Sub-Title2", "{{{パフォーマンス名}}}"], ["Sub-Title3", "{{{公演名副題}}}"], ["Sub-Date", "{{{開催日s}}}"], ["Sub-OpenTime", "{{{開場時刻s}}}"], ["Sub-StartTime", "{{{開始時刻s}}}"], ["Sub-Price", "{{{チケット価格}}}"], ["Sub-Seat1", "{{{券種名}}}"], ["Sub-Seat2", ""], ["Sub-Seat3", ""], ["Sub-Seat4", ""], ["Sub-Seat5", ""]]')''')


def downgrade():
    op.drop_table('FamiPortTicketTemplate')
