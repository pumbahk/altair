"""we need salessegment kind

Revision ID: 1ac1e1ebe04a
Revises: 2cb750d9410a
Create Date: 2013-03-07 11:57:57.941513

"""

# revision identifiers, used by Alembic.
revision = '1ac1e1ebe04a'
down_revision = '2cb750d9410a'

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table('salessegment_kind',
                    sa.Column('organization_id', sa.Integer(), nullable=True),
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(length=255), nullable=True),
                    sa.Column('label', sa.Unicode(length=255), nullable=True),
                    sa.Column('publicp', sa.Boolean, nullable=False, default=True),
                    sa.PrimaryKeyConstraint('id'), 
                    sa.UniqueConstraint('name', 'organization_id')
                    )
    op.add_column('salessegment_group', sa.Column('kind_id', sa.Integer(), nullable=True))
    op.create_foreign_key("fk_salessegment_group_to_salessegment_kind", "salessegment_group", "salessegment_kind", ["kind_id"], ["id"])
    op.execute(u"INSERT INTO salessegment_kind (label, name, organization_id, publicp) SELECT case g.kind when 'first_lottery' then '最速抽選' when 'early_lottery' then '先行抽選' when 'early_lottery' then '先行先着' when 'normal' then '一般販売' when 'added_sales' then '追加販売' when 'added_lottery' then '追加抽選' when 'vip' then '関係者' when 'sales_counter' then '窓口販売' else 'その他' end, g.kind as name, e.organization_id as organization_id, 1  from salessegment_group as g join event as e on g.event_id = e.id group by g.kind, e.organization_id;")


def downgrade():
    op.execute("delete from salessegment_kind;")
    op.drop_constraint("fk_salessegment_group_to_salessegment_kind", "salessegment_group", type="foreignkey")
    op.drop_table("salessegment_kind")
    op.drop_column('salessegment_group', 'kind_id')

