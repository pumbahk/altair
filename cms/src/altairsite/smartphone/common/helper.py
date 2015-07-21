# -*- coding: utf-8 -*-
from .const import SalesEnum, get_prefectures

from altaircms.asset.models import ImageAsset
from altaircms.helpers.asset import rendering_object as asset_rendering_object
from altairsite.mobile.core.eventhelper import EventHelper
import logging
from markupsafe import Markup
from altaircms.datelib import get_now

logger = logging.getLogger(__file__)

class SmartPhoneHelper(object):
    def get_area_japanese(self, keyword):
        regions = {
             'hokkaido':u'北海道・東北'
            ,'syutoken':u'首都圏・北関東'
            ,'koshinetsu':u'甲信越・東海'
            ,'kinki':u'近畿・北陸'
            ,'chugoku':u'中国・四国'
            ,'kyusyu':u'九州・沖縄'
        }
        return regions[keyword]

    def get_prefecture_japanese(self, keyword):
        areas = {
             'hokkaido':u'北海道'
            ,'aomori':u'青森'
            ,'iwate':u'岩手'
            ,'akita':u'秋田'
            ,'miyagi':u'宮城'
            ,'yamagata':u'山形'
            ,'fukushima':u'福島'
            ,'chiba':u'千葉'
            ,'tokyo':u'東京'
            ,'kanagawa':u'神奈川'
            ,'ibaraki':u'茨城'
            ,'tochigi':u'栃木'
            ,'gunma':u'群馬'
            ,'saitama':u'埼玉'
            ,'yamanashi':u'山梨'
            ,'nagano':u'長野'
            ,'niigata':u'新潟'
            ,'gifu':u'岐阜'
            ,'aichi':u'愛知'
            ,'mie':u'三重'
            ,'shizuoka':u'静岡'
            ,'kyoto':u'京都'
            ,'osaka':u'大阪'
            ,'hyogo':u'兵庫'
            ,'shiga':u'滋賀'
            ,'nara':u'奈良'
            ,'wakayama':u'和歌山'
            ,'toyama':u'富山'
            ,'ishikawa':u'石川'
            ,'fukui':u'福井'
            ,'hiroshima':u'広島'
            ,'okayama':u'岡山'
            ,'tottori':u'鳥取'
            ,'shimane':u'島根'
            ,'yamaguchi':u'山口'
            ,'tokushima':u'徳島'
            ,'kagawa':u'香川'
            ,'ehime':u'愛媛'
            ,'kouchi':u'高知'
            ,'okinawa':u'沖縄'
            ,'fukuoka':u'福岡'
            ,'saga':u'佐賀'
            ,'nagasaki':u'長崎'
            ,'kumamoto':u'熊本'
            ,'oita':u'大分'
            ,'miyazaki':u'宮崎'
            ,'kagoshima':u'鹿児島'
        }

        if keyword not in areas:
            return ""

        return areas[keyword]

    def get_sale_japanese(self, key):
        sales = {
             SalesEnum.ALL.v:u'すべてのチケット'
            ,SalesEnum.GENRE.v:u'このジャンルで'
            ,SalesEnum.NEAR_SALE_END.v:u'まもなく終了のチケット'
            ,SalesEnum.ON_SALE.v:u'販売中'
            ,SalesEnum.SOON_ACT.v:u'まもなく開演のチケット'
            ,SalesEnum.WEEK_SALE.v:u'今週発売のチケット'
        }
        return sales[key]

    def get_sales_segment_japanese(self, key):
        segments = {
             "normal":u"一般発売"
            ,"precedence":u"先行販売"
            ,"lottery":u"先行抽選"
        }
        return segments[key]

    def get_week_map(self):
        return {0:u'月',1:u'火',2:u'水',3:u'木',4:u'金',5:u'土',6:u'日'}

    def disp_date(self, target_date):
        disp_str = str(target_date.year) + '/' + str(target_date.month).zfill(2) + '/' \
                       + str(target_date.day).zfill(2)
        return disp_str

    def public_salessegments(self, target_event):
        times = []
        for group in target_event.salessegment_groups:
            if group.publicp:
                for salessegment in group.salessegments:
                    if salessegment.publicp:
                        times.append(salessegment)
        return times

    def disp_salessegment_start_on_date_week(self, target_event):
        times = self.public_salessegments(target_event)

        disp_str = ""
        if len(times) > 0:
            start_on = ""
            for time in times:
                if not start_on:
                    start_on = time.start_on

                if start_on > time.start_on:
                    start_on = time.start_on

            disp_str = self.disp_date_week(start_on)

        return disp_str

    def disp_salessegment_end_on_date_week(self, target_event):
        times = self.public_salessegments(target_event)

        disp_str = ""
        if len(times) > 0:
            end_on = ""
            for time in times:
                if not end_on:
                    end_on = time.end_on

                if end_on < time.end_on:
                    end_on = time.end_on

            disp_str = self.disp_date_week(end_on)

        return disp_str


    def disp_date_week(self, target_date):
        week = self.get_week_map()
        disp_str = str(target_date.year) + '/' + str(target_date.month).zfill(2) + '/' \
                       + str(target_date.day).zfill(2) + '(' + week[target_date.weekday()] + ')'
        return disp_str

    def disp_time(self, target_date):
        week = self.get_week_map()
        disp_str = str(target_date.year) + '/' + str(target_date.month).zfill(2) + '/' \
                   + str(target_date.day).zfill(2) + '(' + week[target_date.weekday()] + ')'\
                   + ' ' + str(target_date.hour).zfill(2) + ':' + str(target_date.minute).zfill(2)
        return disp_str

    def disp_error(self, form):
        for error in form.word.errors:
            return error
        return ""

    def disp_date_error(self, form):
        for field in form:
            if field.name != "word":
                for error in field.errors:
                    if error:
                        return error
        return ""

    def nl2br(self, value):
        return value.replace("\n", "<br />")

    def Markup(self, value):
        return Markup(value)

    def get_event_from_linked_page_id(self, request, linked_page_id):
        helper = EventHelper()
        event = helper.get_event_from_linked_page_id(request=request, linked_page_id=linked_page_id)
        return event

    def get_events_from_hotword(self, request, hotword):
        helper = EventHelper()
        event = helper.get_events_from_hotword(request=request, hotword=hotword)
        return event

    def get_image_asset(self, request, id):
        image_asset = request.allowable(ImageAsset).filter(ImageAsset.id == id).first()
        return image_asset

    def get_asset_rendering_object(self, request, asset):
        return asset_rendering_object(request, asset)

    def now(self, request):
        return get_now(request)

    def get_info(self, event_info, label):
        content = None
        if event_info['event']:
            for item in event_info['event']:
                if item['label'].find(label) != -1:
                    return item['content']
        return content

    def get_info_list(self, event_info, label):
        contents = []
        if event_info['event']:
            for item in event_info['event']:
                if item['label'].find(label) != -1:
                    contents.append((item['label'], item['content']))
        return contents

    def get_venue_cnt(self, event):
        venues = []
        for perf in event.performances:
            if not perf.venue in venues:
                venues.append(perf.venue)
        return len(venues)

    def get_venue_name(self, event, query):
        venue = event.performances[0].venue
        prefectures = get_prefectures(query.area)
        if hasattr(query, "area"):
            for perf in event.performances:
                for pref in prefectures:
                    if perf.prefecture == pref:
                        return perf.venue
        return venue

    def get_summary_salessegment_group(self, event):
        helper = EventHelper()
        return helper.get_summary_salessegment_group(event)

    def disp_period(self, open_time, close):
        if open_time is not None and close is not None and \
           (open_time.year == close.year and open_time.month == close.month and open_time.day == close.day):
            period = self.disp_time(open_time)
        else:
            # 公演日と、公演終了日が違う場合は、両方表示する
            period = u'%s〜%s' % (
                self.disp_date_week(open_time) if open_time is not None else u'',
                self.disp_date_week(close) if close is not None else u'',
                )
        return period
