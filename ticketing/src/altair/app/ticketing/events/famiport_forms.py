# encoding: utf-8
from wtforms.validators import Required, Length, Regexp
from altair.formhelpers.form import OurForm
from altair.formhelpers.fields import OurTextField, OurSelectField, DelimitedTextsField, OurDateTimeField, OurBooleanField
from altair.formhelpers.widgets import OurTextArea
from altair.formhelpers.validators import LengthInSJIS, Katakana, DynSwitchDisabled, Zenkaku
from altair.sqlahelper import get_db_session
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.core.models import Site
from altair.app.ticketing.helpers.base import label_text_for
from altair.app.ticketing.famiport.models import FamiPortSalesChannel, FamiPortPerformanceType
from altair.app.ticketing.famiport.userside_models import AltairFamiPortVenue, AltairFamiPortPerformanceGroup, AltairFamiPortPerformance
from altair.app.ticketing.famiport.api import get_genre_1_list, get_genre_2_list

sales_channels = [
    (FamiPortSalesChannel.FamiPortOnly.value, u'直販のみ'),
    (FamiPortSalesChannel.WebOnly.value, u'予済のみ'),
    (FamiPortSalesChannel.FamiPortAndWeb.value, u'直販と予済'),
    ]

performance_types = [
    (FamiPortPerformanceType.Normal.value, u'通常'),
    (FamiPortPerformanceType.Spanned.value, u'期間内有効'),
    ]

class AltairFamiPortVenueForm(OurForm):
    def sites(field):
        return [
            (site.id, site.name)
            for site in field.form.slave_session.query(Site)
            ]

    site_id = OurSelectField(
        validators=[Required()],
        choice=sites
        )
    name = OurTextField(
        validators=[
            Required(),
            LengthInSJIS(max=50),
            ]
        )
    name_kana = OurTextField(
        validators=[
            Required(),
            Katakana,
            LengthInSJIS(max=100),
            ]
        )

    def slave_session(self):
        return get_db_session(self.request, 'slave')

    def __init__(self, *args, **kwargs):
        context = kwargs.pop('context')
        self.context = context
        self.request = context.request
        super(AltairFamiPortVenueForm, self).__init__(*args, **kwargs)

 
class AltairFamiPortPerformanceGroupForm(OurForm):
    def genre_list(field):
        genre_1_list = get_genre_1_list(field.form.request)
        genre_2_map = {}
        for code_1, code_2, name in get_genre_2_list(field.form.request):
            l = genre_2_map.get(code_1)
            if l is None:
                genre_2_map[code_1] = l = []
            l.append((code_2, name))
        retval = []
        for code_1, name in genre_1_list:
            l = genre_2_map.get(code_1)
            if l is not None:
                for code_2, name_2 in l:
                    retval.append((u'%s-%s' % (code_1, code_2), u'[%s-%s] %s-%s' % (code_1, code_2, name, name_2)))
            else:
                retval.append((u'%s' % code_1, u'[%s] %s' % (code_1, name)))
        return retval


    name_1 = OurTextField(
        label=label_text_for(AltairFamiPortPerformanceGroup.name_1),
        validators=[
            Required(),
            Zenkaku,
            LengthInSJIS(max=80)
            ]
        )
    name_2 = OurTextField(
        label=label_text_for(AltairFamiPortPerformanceGroup.name_2),
        validators=[
            Zenkaku,
            LengthInSJIS(max=80)
            ]
        )
    sales_channel = OurSelectField(
        label=label_text_for(AltairFamiPortPerformanceGroup.sales_channel),
        validators=[Required()],
        choices=sales_channels,
        coerce=int
        )
    genre_code = OurSelectField(
        label=u'ジャンル (直販用)',
        validators=[],
        choices=genre_list
        )
    keywords = DelimitedTextsField(
        label=u'キーワード (直販用)',
        canonical_delimiter=ur' ',
        delimiter_pattern=ur'(?:　| |\t|\r\n|\r|\n)+',
        validators=[
            ],
        widget=OurTextArea()
        )
    search_code = OurTextField(
        label=u'検索コード (直販用)',
        validators=[
            Regexp(ur'^[0-9a-zA-Z]*$'),
            Length(max=20),
            ]
        )

    def slave_session(self):
        return get_db_session(self.request, 'slave')

    def __init__(self, *args, **kwargs):
        context = kwargs.pop('context')
        self.context = context
        self.request = context.request
        super(AltairFamiPortPerformanceGroupForm, self).__init__(*args, **kwargs)


class AltairFamiPortPerformanceForm(OurForm):
    type = OurSelectField(
        label=label_text_for(AltairFamiPortPerformance.type),
        validators=[Required()],
        choices=performance_types,
        coerce=int
        )
    name = OurTextField(
        label=label_text_for(AltairFamiPortPerformance.name),
        validators=[
            Required(),
            Zenkaku,
            LengthInSJIS(max=60)
            ]
        )
    searchable = OurBooleanField(
        label=label_text_for(AltairFamiPortPerformance.searchable)
        )
    start_at = OurDateTimeField(
        label=label_text_for(AltairFamiPortPerformance.start_at),
        validators=[
            DynSwitchDisabled(u'{type} <> "%d"' % FamiPortPerformanceType.Normal.value)
            ]
        )
    ticket_name = OurTextField(
        label=label_text_for(AltairFamiPortPerformance.ticket_name),
        validators=[
            DynSwitchDisabled(u'{type} <> "%d"' % FamiPortPerformanceType.Spanned.value)
            ]
        )

    def slave_session(self):
        return get_db_session(self.request, 'slave')

    def __init__(self, *args, **kwargs):
        context = kwargs.pop('context')
        self.context = context
        self.request = context.request
        super(AltairFamiPortPerformanceForm, self).__init__(*args, **kwargs)


