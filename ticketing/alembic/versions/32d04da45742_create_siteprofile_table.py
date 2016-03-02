# encoding:utf-8
"""Create SiteProfile table

Revision ID: 32d04da45742
Revises: 9538f560df2
Create Date: 2016-02-24 12:51:36.801915

"""

# revision identifiers, used by Alembic.
revision = '32d04da45742'
down_revision = '9538f560df2'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table(
        'SiteProfile',
        sa.Column('id', Identifier, primary_key=True, autoincrement=True),
        sa.Column('name', sa.Unicode(255)),
        sa.Column('zip', sa.Unicode(32)),
        sa.Column('prefecture', sa.Unicode(64), nullable = False),
        sa.Column('city', sa.Unicode(255)),
        sa.Column('street', sa.Unicode(255)),
        sa.Column('address', sa.Unicode(255)),
        sa.Column('other_address', sa.Unicode(255)),
        sa.Column('tel_1', sa.String(32)),
        sa.Column('tel_2', sa.String(32)),
        sa.Column('fax', sa.String(32)),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True)
        )

    # Set up SiteProfile data from existing data in Site
    insert_default_siteprofile_sql = u"INSERT INTO SiteProfile (name, prefecture, updated_at) VALUES ('dummy', '全国', now());"
    op.execute(insert_default_siteprofile_sql)
    insert_siteprofile_sql = u"INSERT INTO SiteProfile (name, prefecture, updated_at) SELECT DISTINCT name, prefecture, now() FROM Site WHERE prefecture is not NULL;"
    op.execute(insert_siteprofile_sql)

    # Set up Site.siteprofile_id with SiteProfile data created above
    op.add_column('Site', sa.Column('siteprofile_id', Identifier, nullable=False))
    update_site_sql = u"UPDATE Site as s, SiteProfile as sp SET s.siteprofile_id = sp.id, s.updated_at = now() \
                        WHERE s.name = sp.name AND s.prefecture = sp.prefecture AND s.prefecture is not NULL;"
    op.execute(update_site_sql)
    update_null_prefecture_site_sql = u"UPDATE Site as s, SiteProfile as sp SET s.siteprofile_id = sp.id, s.updated_at = now() \
                                        WHERE sp.name = 'dummy' AND s.prefecture is NULL;"
    op.execute(update_null_prefecture_site_sql)
    op.create_foreign_key('Site_ibfk_1', 'Site', 'SiteProfile', ['siteprofile_id'], ['id'])

    # Set up AltairFamiPortVenue.siteprofile_id based on existing data in AltairFamiPortVenue_Site
    op.add_column('AltairFamiPortVenue', sa.Column('siteprofile_id', Identifier, nullable=False))
    update_altairfamiportvenue_sql = u"UPDATE AltairFamiPortVenue as afv INNER JOIN AltairFamiPortVenue_Site as afvs on afv.id = afvs.altair_famiport_venue_id \
                                       INNER JOIN Site as s on afvs.site_id = s.id \
                                       INNER JOIN SiteProfile as sp on s.siteprofile_id = sp.id \
                                       SET afv.siteprofile_id = sp.id"
    op.execute(update_altairfamiportvenue_sql)

    # Unique constraint: (siteprofile_id, venue_name) on AltairFamiPortVenue is intentionally left unset
    # considering existing data and logical deletability of AltairFamiPortVenue


def downgrade():
    # op.drop_constraint('AltairFamiPortVenue_ibuq_1', 'AltairFamiPortVenue', 'unique')
    op.drop_column('AltairFamiPortVenue', 'siteprofile_id')
    op.drop_constraint('Site_ibfk_1', 'Site', 'foreignkey')
    op.drop_column('Site', sa.Column('siteprofile_id'))
    op.drop_table('SiteProfile')
