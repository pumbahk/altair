# -*- coding:utf-8 -*-

"""
89ers用のデータ作成。巨大になったら死亡
"""
import itertools
import sys
import functools
import sqlalchemy as sa
from pyramid.decorator import reify
from datetime import datetime

import tableau as t
from tableau.sqla import newSADatum
from tableau import DataWalker
from tableau.sql import SQLGenerator
from altaircms.scripts.misc.dataset import DataSuite, WithCallbackDataSet

import sqlahelper
import altaircms.models

import altaircms.event.models
import altaircms.page.models
import altaircms.topic.models
import altaircms.layout.models


def build_dict(items, k):
    return {getattr(e, k):e for e in items}

class FixtureBuilder(object):
    def __init__(self, Datum):
        class _Datum(Datum):
            def __init__(self, schema, **fields):
                Datum.__init__(self, schema, t.auto("id"), **fields)
        self.Datum = _Datum
        self._Datum = Datum

        class Default(object):
            created_at=datetime(1900, 1, 1)
            updated_at=datetime(1900, 1, 1) 
            publish_begin=datetime(1900, 1, 1)
            today = datetime(2007, 7, 29)
            next_year = datetime(3007, 7, 29)
        self.Default = Default

class Result(object):
    def __init__(self, result, cache):
        self.result = result
        self.cache = cache

    def __iter__(self):
        return iter(self.result)

class Bj89ersFixtureBuilder(FixtureBuilder):
    def __init__(self, Datum):
        """
        layout_triples: (title, template_filename, blocks)
        page_triples: (name, url, layout, structure)
        category_items: (orderno, name, label, hierarchy, page_name)
        topic_items: (orderno, kind, subkind, title, text, )
        """
        super(Bj89ersFixtureBuilder, self).__init__(Datum)
        layout_triples = [
            (u'89ersシンプル', '89ers.base.mako', '[["header"], ["kadomaru"]]'),
            (u'89ersチケットトップ', '89ers.complex.mako', '[["above_kadomaru"],["kadomaru"],["below_kadomaru"]]'),
            (u'89ers.introduction', '89ers.introduction.mako', '[["above_kadomaru"],["card_and_QR"],["card_and_seven"],["card_and_home"],["anshin_and_QR"],["anshin_and_seven"],["anshin_and_home"],["seven_and_seven"]]'),
            (u'89ers:kadomaru2', '89ers.kadomaru2.mako', '[["above_kadomaru"],["kadomaru"],["kadomaru2"],["below_kadomaru"]]'),
            (u'89ers:kadomaru3', '89ers.kadomaru3.mako', '[["above_kadomaru"],["kadomaru"],["kadomaru2"],["kadomaru3"],["below_kadomaru"]]'),
            (u'89ers:kadomaru4', '89ers.kadomaru4.mako', '[["above_kadomaru"],["kadomaru"],["kadomaru2"],["kadomaru3"],["kadomaru4"],["below_kadomaru"]]'),
            (u'89ers:kadomaru5', '89ers.kadomaru5.mako', '[["above_kadomaru"],["kadomaru"],["kadomaru2"],["kadomaru3"],["kadomaru4"],["kadomaru5"],["below_kadomaru"]]')
            ]
        self.layout_triples = layout_triples

        ## structureひどい.
        page_triples = [
            (u'89ers:チケットトップ', 'top', u'89ersチケットトップ','{"above_kadomaru": [], "kadomaru": [{"pk": null, "name": "image"}], "below_kadomaru": [{"pk": null, "name": "freetext"}, {"pk": null, "name": "freetext"}]}'),
            (u'89ers:チケット購入・引き取り方法', "howto", u"89ers.introduction", '{"seven_and_seven": [{"pk": null, "name": "image"}, {"pk": null, "name": "freetext"}, {"pk": null, "name": "freetext"}], "anshin_and_seven": [{"pk": null, "name": "image"}, {"pk": null, "name": "freetext"}, {"pk": null, "name": "freetext"}], "above_kadomaru": [{"pk": null, "name": "heading"}], "card_and_seven": [{"pk": null, "name": "image"}, {"pk": null, "name": "freetext"}, {"pk": null, "name": "freetext"}], "card_and_home": [{"pk": null, "name": "image"}, {"pk": null, "name": "freetext"}, {"pk": null, "name": "freetext"}], "anshin_and_QR": [{"pk": null, "name": "image"}, {"pk": null, "name": "freetext"}, {"pk": null, "name": "freetext"}], "anshin_and_home": [{"pk": null, "name": "image"}, {"pk": null, "name": "freetext"}, {"pk": null, "name": "freetext"}], "card_and_QR": [{"pk": null, "name": "heading"}, {"pk": null, "name": "freetext"}, {"pk": null, "name": "heading"}, {"pk": null, "name": "image"}, {"pk": null, "name": "freetext"}, {"pk": null, "name": "freetext"}]}'),
            (u'89ers:ブースタークラブ申込', 'purcharsed/seven', u'89ersシンプル', '{}'),
            (u'89ers:よくある質問', 'faq', u'89ersシンプル', '{"header": [], "kadomaru": [{"pk": null, "name": "heading"}, {"pk": null, "name": "heading"}, {"pk": null, "name": "topic"}, {"pk": null, "name": "heading"}, {"pk": null, "name": "topic"}, {"pk": null, "name": "heading"}, {"pk": null, "name": "topic"}]}'),
            (u'89ers:価格座席図', "price", u"89ers:kadomaru2", '{"above_kadomaru": [{"pk": null, "name": "heading"}], "kadomaru": [{"pk": null, "name": "heading"}, {"pk": null, "name": "freetext"}], "below_kadomaru": [], "kadomaru2": [{"pk": null, "name": "heading"}, {"pk": null, "name": "image"}, {"pk": null, "name": "freetext"}, {"pk": null, "name": "freetext"}, {"pk": null, "name": "freetext"}]}'), 
            (u'89ers:残席情報', "unocurppied", u"89ersチケットトップ", '{"above_kadomaru": [{"pk": null, "name": "heading"}], "kadomaru": [{"pk": null, "name": "heading"}, {"pk": null, "name": "freetext"}, {"pk": null, "name": "freetext"}], "below_kadomaru": []}'), 
            (u'89ers:チケット取り扱い数量', "playguide", u"89ersシンプル", '{}'), 
            (u'89ers:チケット購入', "purchase", u"89ers:kadomaru4", '{"above_kadomaru": [{"pk": null, "name": "heading"}], "kadomaru4": [{"pk": null, "name": "heading"}, {"pk": null, "name": "freetext"}], "kadomaru3": [{"pk": null, "name": "heading"}, {"pk": null, "name": "image"}, {"pk": null, "name": "freetext"}, {"pk": null, "name": "freetext"}, {"pk": null, "name": "freetext"}], "kadomaru2": [{"pk": null, "name": "heading"}, {"pk": null, "name": "freetext"}], "kadomaru": [{"pk": null, "name": "freetext"}, {"pk": null, "name": "heading"}, {"pk": null, "name": "freetext"}, {"pk": null, "name": "heading"}, {"pk": null, "name": "freetext"}], "below_kadomaru": []}')]
            ]
        self.page_triples = page_triples

        topic_items = [
            (1, u"89ers質問", u"チケット引取について", u"ナイナーズチケットには、どのようなチケット引取方法がありますか？", u"チケット引取方法として、① 携帯電話にQRコードをメール送信、② QRコードをプリンターでプリントアウトの他に、③ セブン-イレブンでの発券（別途手数料105円／1枚）、④ 自宅へ配送（別途手数料630円／1申込）、といった方法がございます。", u'89ers:よくある質問'),
            (2, u"89ers質問", u"チケット引取について", u"QRコードでの受取を選んだ場合、どのようにチケットを受け取れますか？", u"ナイナーズチケットではチケット購入完了後、チケット情報が組み込まれたQRコードが発行されます。このQRコードを携帯電話にメール送信する、もしくは自宅プリンターでプリントアウトし、試合日当日に会場までお持ちください。窓口にて、実券と引換いたします。", u'89ers:よくある質問'),
            (3, u"89ers質問", u"チケット引取について", u"ナイナーズチケットで「セブン-イレブン」受取を選んだ場合、いつまでに受取ればいいでしょうか？", u"試合日当日まで引換が可能です。全国どこのセブン-イレブンでも受取が可能です。なお、セブン-イレブンでのお支払いを選んだ場合、ご予約後、予約日時の3日間（72時間）以内にお支払が必要です。それを過ぎますと、予約が自動的にキャンセルとなります。詳細は予約完了メールでご確認ください。", u'89ers:よくある質問'),
            (1, u"89ers質問", u"ナイナーズチケットについて", u"ナイナーズチケットとは？", u"座席指定、24時間購入可能、QRコードでの発券なら手数料が無料、とチケット購入がより便利になったチケットです！チームがチケットを直接販売するシステムです。", u'89ers:よくある質問'),
            (2, u"89ers質問", u"ナイナーズチケットについて", u"ナイナーズチケットはどうやって利用するのですか？", u"ナイナーズチケットは、インターネット（パソコン、携帯電話）環境があればご利用いただけます。チーム公式ホームページ、公式携帯サイトからナイナーズチケット専用ページへお進みください。", u'89ers:よくある質問'),
            (3, u"89ers質問", u"ナイナーズチケットについて", u"ナイナーズチケットはいつから利用できるのですか？", u"チケット発売初日、午前10時から、ご利用可能です。<a href=\"/top\">チケット販売スケジュールはこちらをご覧ください。</a>", u'89ers:よくある質問'),
            (4, u"89ers質問", u"ナイナーズチケットについて", u"夜中でもナイナーズチケットは利用できるのですか？", u"ナイナーズチケットは24時間いつでもチケット購入が可能です（不定期にシステムメンテナンス時間を設けさせていただく場合がございます）。", u'89ers:よくある質問'),
            (5, u"89ers質問", u"ナイナーズチケットについて", u"ブースタークラブ先行販売へ参加するには？", u"ゴールド・プラチナ・レギュラーのいずれかのブースタークラブへ入会が必要になります。<br />入会特典として、一般発売に先駆け、チケット先行予約に参加いただけます。\n豪華特典満載のブースタークラブへの入会は<a href=\"http://www.89ers.jp/booster/index.html\" target=\"_blank\">こちら</a>から！", u'89ers:よくある質問'),
            (1, u"89ers質問", u"購入について", u"チケットの発売日はいつですか？", u"<a href=\"/top\">チケ ット販売スケジュールはこちらをご覧ください。</a>2012-2013シーズン開幕戦については、9月1日の10:00から発売開始を予定しています。", u'89ers:よくある質問'),
            (2, u"89ers質問", u"購入について", u"ナイナーズチケット以外で、チケットはどこで買えますか？", u"ローソン、チケットぴあ、イープラス、河北チケットセンターで販売しております。", u'89ers:よくある質問'),
            (3, u"89ers質問", u"購入について", u"ナイナーズチケットでの決済方法はどうすれば良いですか？", u"クレジットカード決済(通常のカード決済あるいは「楽天あんしん支払いサービス」でのカード決済)とセブン-イレブン店頭でのお支払が可能です。 購入手続きと同時に、ご指定の決済方法で代金を決済していただきます。なお、支払方法・引取方法により手数料がかかる場合があります 。", u'89ers:よくある質問'),
            (4, u"89ers質問", u"購入について", u"クレジットカードを持っていません。 どうすれば良いですか？", u"ナイナーズチケットでは、決済方法としてセブン-イレブン店頭での支払を選択できます。（対象試合日4日前まで受付） なおその場合、お客様に別途手数料として1申込あたり158円をご負担いただくことになりますので予めご了承ください。チケット予約時に発行される払込票番号をお引換え期限内にセブン-イレブンのレジへお持ちください。チケット代金はセブン-イレブンのレジにてお支払ください。", u'89ers:よくある質問'),
            (5, u"89ers質問", u"購入について", u"ナイナーズチケットで、友達の分も一緒にQRコード受取で購入したい。どうすれば良いですか？", u"QRコードは各チケット毎に発行されます（チケット4枚購入の場合、4つのQRコードが発行されます）。ご一緒される方のアドレスを予めご用意のうえ、ご操作ください（ご一緒される方のアドレスに転送が可能です）", u'89ers:よくある質問'),
            (6, u"89ers質問", u"購入について", u"購入完了メールが届きません。どうすれば良いですか？", u"しばらく経ってもメールが届かない場合には、「お名前」「ご登録のお電話番号」をお書き添えの上、 <a href=\"89ers_support@ticketstar.jp\" target=\"_blank\">89ers_support@ticketstar.jp</a> までお問い合わせください。<br />\nなお、購入完了メールや、お問い合わせに対する返信は @ticketstar.jp のドメインから送信しています。ハピチケからのメールが受信できるよう、パソコンや携帯でのドメイン指定の設定をお願いいたします。", u'89ers:よくある質問'),
            (7, u"89ers質問", u"購入について", u"ナイナーズチケットでチケットを購入したのですが、QRコードが届きません。もう一度送ることができないのですか？", u"購入履歴確認ページより再度送信することができます。また、購入履歴確認ページではご購入いただいた試合の確認なども行えます。", u'89ers:よくある質問'),
            (8, u"89ers質問", u"購入について", u"チケット購入履歴を確認したい。 どうすれば良いですか？", u"ご購入内容は、購入履歴確認ページより確認できます。 受付番号が分かる場合、受付番号・購入時登録電話番号を入力してください。 受付番号が不明な場合は、お手数ですが、 <a href=\"89ers_support@ticketstar.jp\" target=\"_blank\">89ers_support@ticketstar.jp</a> までお問合せください。", u'89ers:よくある質問'),
            (9, u"89ers質問", u"購入について", u"チケットのキャンセル・座席変更は可能ですか？", u"チケット購入後のキャンセル・変更は行えません。ご了承ください。", u'89ers:よくある質問'),
            (10, u"89ers質問", u"購入について", u"車椅子席のチケットを購入したいのですが、どうすれば良いですか？", u"仙台 89ERS　チケット事務局（TEL：022-215-8138）までお問合せください（平日：9:00〜18:00）。", u'89ers:よくある質問'),
            (11, u"89ers質問", u"購入について", u"何歳からチケットは必要ですか？", u"4歳以上のお子様はチ ケットが必要となります。 ただし、3歳以下のお子様でも一人で着席をご希望の場合はチケットが必要です。", u'89ers:よくある質問'),
            ]
        self.topic_items = topic_items

        category_items = [
            (1, "top", u"チケットTOP", "header_menu", u"89ers:チケットトップ", ), 
            (2, "howto", u"購入・引き取り方法", "header_menu", u"", ), 
            (3, "purchase", u"チケット購入", "header_menu", u"", ), 
            (3, "faq", u"FAQ", "header_menu", u"", ), 
            (4, "price", u"価格・座席図", "header_menu", u"", ), 
            (5, "unoccupied", u"残席情報", "header_menu", u"", ), 
            (6, "playguide", u"チケット取扱数量", "header_menu", u"", ), 

            (2, "order_way",  u"チケット購入・引き取り方法", "header_menu", u"89ers:チケット購入・引き取り方法"), 
            (3, "register_club",  u"ブースタークラブ申込", "header_menu", u"89ers:ブースタークラブ申込"), 
            (4, "faq",  u"よくある質問", "header_menu", u"89ers:よくある質問"), 
            ]
        self.category_items = category_items
        self.organization_id = 3 ## fixme

    @reify
    def build_layout(self):
        retval =  [self.Datum("layout", 
                           title=title, 
                           template_filename=template_filename, 
                           blocks=blocks, 
                           organization_id=self.organization_id, 
                           created_at=self.Default.created_at, 
                           updated_at=self.Default.updated_at)\
                       for title, template_filename, blocks in self.layout_triples]
        result = Result(retval, build_dict(retval, "title"))
        return result

    @reify
    def build_pageset(self):
        retval = [self.Datum("pagesets", 
                             name=name, 
                             organization_id=self.organization_id, 
                             version_counter=0, 
                             url=url)\
                      for name, url, layout_name in self.page_triples]
        result = Result(retval, build_dict(retval, "name"))
        return result

    @reify
    def build_page(self):       
        layouts = self.build_layout.cache
        pagesets = self.build_pageset.cache
        retval = [self.Datum("page", 
                  name=name, 
                  title=name, 
                  url=url, 
                  description="", 
                  pageset=t.many_to_one(pagesets[name], "pageset_id"), 
                  keywords="", 
                  structure="{}", 
                  version=0, 
                  published=True, 
                  publish_begin=self.Default.publish_begin, 
                  created_at=self.Default.created_at, 
                  updated_at=self.Default.updated_at, 
                  organization_id=self.organization_id, 
                  layout_id=layouts[layout_name])
                      for name, url, layout_name in self.page_triples]
        result = Result(retval, build_dict(retval, "name"))
        return result
        
    @reify
    def build_category(self):
        pagesets = self.build_pageset.cache
        retval = [self.Datum("category", 
                             orderno=orderno, 
                             organization_id=self.organization_id, 
                             name=name, 
                             label=label, 
                             hierarchy=hierarchy, 
                             pageset_id=pagesets.get(page_name)
                             )
                  for orderno, name, label, hierarchy, page_name in self.category_items]
        result = Result(retval, build_dict(retval, "name"))
        return result

    @reify
    def build_topic(self):
        pagesets = self.build_pageset.cache
        retval = [self.Datum("topic", 
                             publish_open_on=self.Default.today, 
                             publish_close_on=self.Default.next_year, 
                             kind=kind, 
                             subkind=subkind, 
                             bound_page_id=pagesets[page], 
                             organization_id=self.organization_id, 
                             orderno=orderno, 
                             title=title, 
                             text=text)
                  for orderno, kind, subkind, title, text, page in self.topic_items]
        result = Result(retval, build_dict(retval, "title"))
        return result
    
    def build(self):
        return itertools.chain.from_iterable([
                self.build_layout, 
                self.build_pageset, 
                self.build_page, 
                self.build_category, 
                self.build_topic, 
                ], )
                 
class WithOffset(object):
    """ insert sql id with offset value

    e.g. offset = 10
    insert statment start from id=11
    """
    def __init__(self):
        self.offset_table = {}
        self.session = sqlahelper.get_session()
        self.table_to_declarative = self.collect_declarative(sqlahelper.get_base())

    def collect_declarative(self, base):
        table_to_declarative = {}
        if base is not None:
            for class_name, declarative in base._decl_class_registry.items():
                table_to_declarative[declarative.__table__.name] = declarative
        return table_to_declarative

    def _get_offset_value(self, schema, data):
        cls = self.table_to_declarative[schema]
        return cls.query.with_entities(sa.func.Max(cls.id)).scalar() or 0

    def get_offset_value(self, schema, data): #memoize function
        if not schema in self.offset_table:
            self.offset_table[schema] = self._get_offset_value(schema, data)
        return self.offset_table[schema]
        
    def setvalue(self, data, datum):
        schema = datum._tableau_table.name
        offset = self.get_offset_value(schema, datum)
        pk = data.seq + offset
        setattr(datum, datum._tableau_id_fields[0], pk)
        assert getattr(datum, datum._tableau_id_fields[0], pk)

def main(args):
    sqlahelper.add_engine(sa.create_engine(args[1]))

    Base = sqlahelper.get_base()
    Datum = newSADatum(Base.metadata, Base)

    builder = Bj89ersFixtureBuilder(Datum)
    suite = DataSuite(dataset_impl=functools.partial(WithCallbackDataSet, on_autoid=WithOffset()))
    walker = DataWalker(suite)

    for datum in builder.build():
        walker(datum)
    SQLGenerator(sys.stdout, encoding='utf-8')(suite)
main(sys.argv)

