# encoding: utf-8

"""add_cart_setting

Revision ID: 41faffc1f5c7
Revises: 347ed51cb0e5
Create Date: 2014-10-24 13:50:20.467331

"""

# revision identifiers, used by Alembic.
revision = '41faffc1f5c7'
down_revision = '347ed51cb0e5'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf
from altair.models import Identifier, JSONEncodedDict
import json
import re

settings_list = [
    dict(
        _organization=u"89ers",
        _type=u"booster.89ers",
        _event_id=1,
        _complete_title=u"仙台89ERS ブースター会員申込",
        _product_name=u"仙台89ERS 2014-2015 クラブナイナーズ",
        flavors=dict(japanese_prefectures=True),
        default_prefecture=u'宮城県',
        title=u"仙台89ERS クラブナイナーズ入会申込ページ",
        contact_url=u"mailto:89ers@tstar.jp",
        contact_url_mobile=u"mailto:89ers@tstar.jp",
        contact_name=u"仙台89ERS　クラブナイナーズ事務局",
        contact_tel=u"022-215-8138",
        contact_office_hours=u"平日：9:00〜18:00",
        mobile_header_background_color=u'#ffb700',
        mobile_marker_color=u'#ffb700',
        mobile_required_marker_color=u'#ff0000',
        fc_announce_page_url= u'http://www.89ers.jp/',
        fc_announce_page_title = u"89ers公式ホームページへ",
        privacy_policy_page_url=u"http://ticketstar.jp/privacy",
        privacy_policy_page_url_mobile=u"http://ticketstar.jp/privacy",
        legal_notice_page_url=u'http://www.ticketstar.jp/legal',
        legal_notice_page_url_mobile=u'http://www.ticketstar.jp/legal',
        orderreview_page_url=u"https://89ers.tstar.jp/orderreview",
        mail_filter_domain_notice_template=u'※注文受付完了、確認メール等をメールでご案内します。「{domain}」からのメールを受信できるよう、お申し込み前にドメイン指定の設定を必ずお願いいたします。'
        ),
    dict(
        _organization=u"BT",
        _type=u"booster.bambitious",
        _event_id=1567,
        _complete_title=u"バンビシャス奈良 ブースタークラブ クラブバンビシャス入会申込",
        _product_name=u"バンビシャス奈良 ブースタークラブ クラブバンビシャス入会申込",
        flavors=dict(japanese_prefectures=True),
        default_prefecture=u'奈良県',
        title=u"シーズン入会受付",
        contact_url=u"mailto:club-bambitious@bambitious.jp",
        contact_url_mobile=u"mailto:club-bambitious@bambitious.jp",
        contact_name=u"クラブバンビシャス事務局",
        contact_tel=u"0742-20-1800",
        contact_office_hours=u"平日：10:00～17:00",
        mobile_header_background_color=u'#a80038',
        mobile_marker_color=u'#a80038',
        mobile_required_marker_color=u'#ff0000',
        fc_announce_page_url= u'http://bambitious.jp/',
        fc_announce_page_title = u"バンビシャス奈良 公式ホームページへ",
        privacy_policy_page_url=u"http://www.ticketstar.jp/privacy/",
        privacy_policy_page_url_mobile=u"http://www.ticketstar.jp/privacy/",
        legal_notice_page_url=u'http://www.ticketstar.jp/legal',
        legal_notice_page_url_mobile=u'http://www.ticketstar.jp/legal',
        orderreview_page_url=u"https://bambitious.tstar.jp/orderreview",
        mail_filter_domain_notice_template=u'※注文受付完了、確認メール等をメールでご案内します。「{domain}」からのメールを受信できるよう、お申し込み前にドメイン指定の設定を必ずお願いいたします。'
        ),
    dict(
        _organization=u"bigbulls",
        _type=u"booster.bigbulls",
        _event_id=543,
        _complete_title = u"岩手ビッグブルズ クラブブルズ会員入会申込",
        _product_name=u"岩手ビッグブルズ 2014-2015 ブースタークラブ",
        flavors=dict(japanese_prefectures=True),
        default_prefecture=u'岩手県',
        title=u"岩手ビッグブルズ クラブブルズ会員入会申込ページ",
        contact_url=u"mailto:bigbulls@tstar.jp",
        contact_url_mobile=u"mailto:bigbulls@tstar.jp",
        contact_name=u"(株)岩手スポーツプロモーション",
        contact_tel=u"019-622-6811",
        contact_office_hours=u"平日 9:30～18:30",
        mobile_header_background_color=u'#1a395d',
        mobile_marker_color=u'#1a395d',
        mobile_required_marker_color=u'#ff0000',
        fc_announce_page_url= u'http://www.bigbulls.jp/',
        fc_announce_page_title=u"bigbulls公式ホームページへ",
        privacy_policy_page_url=u"http://ticketstar.jp/privacy",
        privacy_policy_page_url_mobile=u"http://ticketstar.jp/privacy",
        legal_notice_page_url=u'http://www.ticketstar.jp/legal',
        legal_notice_page_url_mobile=u'http://www.ticketstar.jp/legal',
        orderreview_page_url=u"https://bigbulls.tstar.jp/orderreview",
        mail_filter_domain_notice_template=u'※注文受付完了、確認メール等をメールでご案内します。「{domain}」からのメールを受信できるよう、お申し込み前にドメイン指定の設定を必ずお願いいたします。'
        )        
    ]

standard_settings_list = [
    {
        "_type": "standard", 
        "_organization": "DJ", 
        "mobile_marker_color": "#FEBF00", 
        "mobile_required_marker_color": "#ff0000", 
        "mobile_header_background_color": "#533B23", 
        "operator_info_url": "http://www.ticketstar.jp", 
        "contact_url": "", 
        "contact_url_mobile": "", 
        "privacy_policy_page_url": "http://www.ticketstar.jp/privacy", 
        "privacy_policy_page_url_mobile": "http://www.ticketstar.jp/privacy",
        "legal_notice_page_url": "http://www.ticketstar.jp/legal",
        "legal_notice_page_url_mobile": "http://www.ticketstar.jp/legal",
        "mail_filter_domain_notice_template": u"予約受付完了メール等をメールでご案内します。「{domain}」からのメールを受信できるよう、お申し込み前にドメイン指定の設定を必ずお願いいたします。",
        }, 
    {
        "_type": "standard", 
        "_organization": "BA", 
        "mobile_marker_color": "#ea9f27", 
        "mobile_required_marker_color": "#ff0000", 
        "mobile_header_background_color": "#09355f", 
        "operator_info_url": "http://www.ticketstar.jp", 
        "contact_url": "", 
        "contact_url_mobile": "", 
        "privacy_policy_page_url": "http://www.ticketstar.jp/privacy", 
        "privacy_policy_page_url_mobile": "http://www.ticketstar.jp/privacy", 
        "legal_notice_page_url": "http://www.ticketstar.jp/legal",
        "legal_notice_page_url_mobile": "http://www.ticketstar.jp/legal",
        "mail_filter_domain_notice_template": u"予約受付完了メール等をメールでご案内します。「{domain}」からのメールを受信できるよう、お申し込み前にドメイン指定の設定を必ずお願いいたします。",
        }, 
    {
        "_type": "standard", 
        "_organization": "BT", 
        "mobile_marker_color": "#a01e23", 
        "mobile_required_marker_color": "#ff0000", 
        "mobile_header_background_color": "#a01e23", 
        "operator_info_url": "http://www.ticketstar.jp/corporate", 
        "contact_url": "mailto:bambitious@tstar.jp", 
        "contact_url_mobile": "mailto:bambitious@tstar.jp", 
        "privacy_policy_page_url": "http://www.ticketstar.jp/privacy", 
        "privacy_policy_page_url_mobile": "http://www.ticketstar.jp/privacy", 
        "legal_notice_page_url": "http://www.ticketstar.jp/legal",
        "legal_notice_page_url_mobile": "http://www.ticketstar.jp/legal",
        "mail_filter_domain_notice_template": u"予約受付完了メール等をメールでご案内します。「{domain}」からのメールを受信できるよう、お申し込み前にドメイン指定の設定を必ずお願いいたします。",
        }, 
    {
        "_type": "standard", 
        "_organization": "JI", 
        "mobile_marker_color": "#FEBF00", 
        "mobile_required_marker_color": "#ff0000", 
        "mobile_header_background_color": "#1D2B62", 
        "operator_info_url": "http://www.ticketstar.jp", 
        "contact_url": "", 
        "contact_url_mobile": "", 
        "privacy_policy_page_url": "http://privacy.rakuten.co.jp/", 
        "privacy_policy_page_url_mobile": "http://privacy.rakuten.co.jp/", 
        "legal_notice_page_url": "http://www.ticketstar.jp/legal",
        "legal_notice_page_url_mobile": "http://www.ticketstar.jp/legal",
        "mail_filter_domain_notice_template": u"予約受付完了メール等をメールでご案内します。「{domain}」からのメールを受信できるよう、お申し込み前にドメイン指定の設定を必ずお願いいたします。",
        }, 
    {
        "_type": "standard", 
        "_organization": "BS", 
        "mobile_marker_color": "#FEBF00", 
        "mobile_required_marker_color": "#ff0000", 
        "mobile_header_background_color": "#9E751E", 
        "operator_info_url": "http://www.ticketstar.jp", 
        "contact_url": "", 
        "contact_url_mobile": "", 
        "privacy_policy_page_url": "http://www.ticketstar.jp/privacy", 
        "privacy_policy_page_url_mobile": "http://www.ticketstar.jp/privacy", 
        "legal_notice_page_url": "http://www.ticketstar.jp/legal",
        "legal_notice_page_url_mobile": "http://www.ticketstar.jp/legal",
        "mail_filter_domain_notice_template": u"予約受付完了メール等をメールでご案内します。「{domain}」からのメールを受信できるよう、お申し込み前にドメイン指定の設定を必ずお願いいたします。",
        }, 
    {
        "_type": "standard", 
        "_organization": "bigbulls", 
        "mobile_marker_color": "#0a1232", 
        "mobile_required_marker_color": "#ff0000", 
        "mobile_header_background_color": "#0a1232", 
        "operator_info_url": "http://www.ticketstar.jp/corporate", 
        "contact_url": "mailto:bigbulls@tstar.jp", 
        "contact_url_mobile": "mailto:bigbulls@tstar.jp", 
        "privacy_policy_page_url": "http://www.ticketstar.jp/privacy", 
        "privacy_policy_page_url_mobile": "http://www.ticketstar.jp/privacy", 
        "legal_notice_page_url": "http://www.ticketstar.jp/legal",
        "legal_notice_page_url_mobile": "http://www.ticketstar.jp/legal",
        "mail_filter_domain_notice_template": u"予約受付完了メール等をメールでご案内します。「{domain}」からのメールを受信できるよう、お申し込み前にドメイン指定の設定を必ずお願いいたします。",
        }, 
    {
        "_type": "standard", 
        "_organization": "YT", 
        "mobile_marker_color": "#AC8B9A", 
        "mobile_required_marker_color": "#ff0000", 
        "mobile_header_background_color": "#892C55", 
        "operator_info_url": "http://www.ticketstar.jp", 
        "contact_url": "http://www.ytj.gr.jp/contact/", 
        "contact_url_mobile": "http://www.ytj.gr.jp/contact/", 
        "privacy_policy_page_url": "http://privacy.rakuten.co.jp/", 
        "privacy_policy_page_url_mobile": "http://privacy.rakuten.co.jp/", 
        "legal_notice_page_url": "http://www.ticketstar.jp/legal",
        "legal_notice_page_url_mobile": "http://www.ticketstar.jp/legal",
        "mail_filter_domain_notice_template": u"予約受付完了メール等をメールでご案内します。「{domain}」からのメールを受信できるよう、お申し込み前にドメイン指定の設定を必ずお願いいたします。",
        }, 
    {
        "_type": "standard", 
        "_organization": "ticketstar", 
        "mobile_marker_color": "#0c4196", 
        "mobile_required_marker_color": "#ff0000", 
        "mobile_header_background_color": "#0c4196", 
        "operator_info_url": "http://www.ticketstar.jp/corporate", 
        "contact_url": "mailto:info@tstar.jp", 
        "contact_url_mobile": "mailto:info@tstar.jp", 
        "privacy_policy_page_url": "http://www.ticketstar.jp/privacy", 
        "privacy_policy_page_url_mobile": "http://www.ticketstar.jp/privacy", 
        "legal_notice_page_url": "http://www.ticketstar.jp/legal",
        "legal_notice_page_url_mobile": "http://www.ticketstar.jp/legal",
        "mail_filter_domain_notice_template": u"予約受付完了メール等をメールでご案内します。「{domain}」からのメールを受信できるよう、お申し込み前にドメイン指定の設定を必ずお願いいたします。",
        }, 
    {
        "_type": "standard", 
        "_organization": "d1", 
        "mobile_marker_color": "#ffb700", 
        "mobile_required_marker_color": "#ff0000", 
        "mobile_header_background_color": "#ffb700", 
        "operator_info_url": "http://www.ticketstar.jp/corporate", 
        "contact_url": "mailto:89ers@tstar.jp", 
        "contact_url_mobile": "mailto:89ers@tstar.jp", 
        "privacy_policy_page_url": "http://www.ticketstar.jp/privacy", 
        "privacy_policy_page_url_mobile": "http://www.ticketstar.jp/privacy", 
        "legal_notice_page_url": "http://www.ticketstar.jp/legal",
        "legal_notice_page_url_mobile": "http://www.ticketstar.jp/legal",
        "mail_filter_domain_notice_template": u"予約受付完了メール等をメールでご案内します。「{domain}」からのメールを受信できるよう、お申し込み前にドメイン指定の設定を必ずお願いいたします。",
        }, 
    {
        "_type": "standard", 
        "_organization": "NH", 
        "mobile_marker_color": "#F12997", 
        "mobile_required_marker_color": "#ff0000", 
        "operator_info_url": "http://www.ticketstar.jp/corporate", 
        "mobile_header_background_color": "#F12997", 
        "contact_url": "mailto:happinets@tstar.jp", 
        "contact_url_mobile": "mailto:happinets@tstar.jp", 
        "privacy_policy_page_url": "http://www.ticketstar.jp/privacy", 
        "privacy_policy_page_url_mobile": "http://www.ticketstar.jp/privacy", 
        "legal_notice_page_url": "http://www.ticketstar.jp/legal",
        "legal_notice_page_url_mobile": "http://www.ticketstar.jp/legal",
        "mail_filter_domain_notice_template": u"予約受付完了メール等をメールでご案内します。「{domain}」からのメールを受信できるよう、お申し込み前にドメイン指定の設定を必ずお願いいたします。",
        }, 
    {
        "_type": "standard", 
        "_organization": "LG", 
        "mobile_marker_color": "#E60048", 
        "mobile_required_marker_color": "#ff0000", 
        "mobile_header_background_color": "#0A50AA", 
        "operator_info_url": "http://www.ticketstar.jp", 
        "contact_url": "", 
        "contact_url_mobile": "", 
        "privacy_policy_page_url": "http://privacy.rakuten.co.jp/", 
        "privacy_policy_page_url_mobile": "http://privacy.rakuten.co.jp/", 
        "legal_notice_page_url": "http://www.ticketstar.jp/legal",
        "legal_notice_page_url_mobile": "http://www.ticketstar.jp/legal",
        "mail_filter_domain_notice_template": u"予約受付完了メール等をメールでご案内します。「{domain}」からのメールを受信できるよう、お申し込み前にドメイン指定の設定を必ずお願いいたします。",
        }, 
    {
        "_type": "standard", 
        "_organization": "PC", 
        "mobile_marker_color": "#FEBF00", 
        "mobile_required_marker_color": "#ff0000", 
        "mobile_header_background_color": "#1D2B62", 
        "operator_info_url": "http://www.ticketstar.jp", 
        "contact_url": "", 
        "contact_url_mobile": "", 
        "privacy_policy_page_url": "http://www.ticketstar.jp/privacy", 
        "privacy_policy_page_url_mobile": "http://www.ticketstar.jp/privacy", 
        "legal_notice_page_url": "http://www.ticketstar.jp/legal",
        "legal_notice_page_url_mobile": "http://www.ticketstar.jp/legal",
        "mail_filter_domain_notice_template": u"予約受付完了メール等をメールでご案内します。「{domain}」からのメールを受信できるよう、お申し込み前にドメイン指定の設定を必ずお願いいたします。",
        }, 
    {
        "_type": "standard", 
        "_organization": "TH", 
        "mobile_marker_color": "#ea9f27", 
        "mobile_required_marker_color": "#ff0000", 
        "mobile_header_background_color": "#09355f", 
        "operator_info_url": "http://www.ticketstar.jp", 
        "contact_url": "", 
        "contact_url_mobile": "", 
        "privacy_policy_page_url": "http://privacy.rakuten.co.jp/", 
        "privacy_policy_page_url_mobile": "http://privacy.rakuten.co.jp/", 
        "legal_notice_page_url": "http://www.ticketstar.jp/legal",
        "legal_notice_page_url_mobile": "http://www.ticketstar.jp/legal",
        "mail_filter_domain_notice_template": u"予約受付完了メール等をメールでご案内します。「{domain}」からのメールを受信できるよう、お申し込み前にドメイン指定の設定を必ずお願いいたします。",
        }, 
    {
        "_type": "standard", 
        "_organization": "TG", 
        "mobile_marker_color": "#ff9900", 
        "mobile_required_marker_color": "#ff0000", 
        "mobile_header_background_color": "#d00000", 
        "operator_info_url": "http://www.ticketstar.jp", 
        "contact_url": "", 
        "contact_url_mobile": "", 
        "privacy_policy_page_url": "http://privacy.rakuten.co.jp/", 
        "privacy_policy_page_url_mobile": "http://privacy.rakuten.co.jp/", 
        "legal_notice_page_url": "http://www.ticketstar.jp/legal",
        "legal_notice_page_url_mobile": "http://www.ticketstar.jp/legal",
        "mail_filter_domain_notice_template": u"予約受付完了メール等をメールでご案内します。「{domain}」からのメールを受信できるよう、お申し込み前にドメイン指定の設定を必ずお願いいたします。",
        }, 
    {
        "_type": "standard", 
        "_organization": "TC", 
        "mobile_marker_color": "#ea9f27", 
        "mobile_required_marker_color": "#ff0000", 
        "mobile_header_background_color": "#9154FF", 
        "operator_info_url": "http://www.ticketstar.jp", 
        "contact_url": "", 
        "contact_url_mobile": "", 
        "privacy_policy_page_url": "http://privacy.rakuten.co.jp/", 
        "privacy_policy_page_url_mobile": "http://privacy.rakuten.co.jp/", 
        "legal_notice_page_url": "http://www.ticketstar.jp/legal",
        "legal_notice_page_url_mobile": "http://www.ticketstar.jp/legal",
        "mail_filter_domain_notice_template": u"予約受付完了メール等をメールでご案内します。「{domain}」からのメールを受信できるよう、お申し込み前にドメイン指定の設定を必ずお願いいたします。",
        }, 
    {
        "_type": "standard", 
        "_organization": "RK", 
        "mobile_marker_color": "#cbae55", 
        "mobile_required_marker_color": "#ff0000", 
        "mobile_header_background_color": "#cbae55", 
        "operator_info_url": "http://www.ticketstar.jp/corporate", 
        "contact_url": "mailto:kings@tstar.jp", 
        "contact_url_mobile": "mailto:kings@tstar.jp", 
        "privacy_policy_page_url": "http://www.ticketstar.jp/privacy", 
        "privacy_policy_page_url_mobile": "http://www.ticketstar.jp/privacy", 
        "legal_notice_page_url": "http://www.ticketstar.jp/legal",
        "legal_notice_page_url_mobile": "http://www.ticketstar.jp/legal",
        "mail_filter_domain_notice_template": u"予約受付完了メール等をメールでご案内します。「{domain}」からのメールを受信できるよう、お申し込み前にドメイン指定の設定を必ずお願いいたします。",
        }, 
    {
        "_type": "standard", 
        "_organization": "RT", 
        "mobile_marker_color": "#990018", 
        "mobile_required_marker_color": "#ff0000", 
        "mobile_header_background_color": "#990018", 
        "operator_info_url": "http://www.ticketstar.jp/corporate", 
        "contact_url": "https://ticket.rakuten.co.jp/inquiry", 
        "contact_url_mobile": "https://ticket.rakuten.co.jp/inquiry", 
        "privacy_policy_page_url": "http://privacy.rakuten.co.jp/", 
        "privacy_policy_page_url_mobile": "http://privacy.rakuten.co.jp/", 
        "legal_notice_page_url": "http://www.ticketstar.jp/legal",
        "legal_notice_page_url_mobile": "http://www.ticketstar.jp/legal",
        "mail_filter_domain_notice_template": u"予約受付完了メール等をメールでご案内します。「{domain}」からのメールを受信できるよう、お申し込み前にドメイン指定の設定を必ずお願いいたします。",
        }, 
    {
        "_type": "standard", 
        "_organization": "CB", 
        "mobile_marker_color": "#ea9f27", 
        "mobile_required_marker_color": "#ff0000", 
        "mobile_header_background_color": "#09355f", 
        "operator_info_url": "http://www.ticketstar.jp", 
        "contact_url": "", 
        "contact_url_mobile": "", 
        "privacy_policy_page_url": "http://www.ticketstar.jp/privacy", 
        "privacy_policy_page_url_mobile": "http://www.ticketstar.jp/privacy", 
        "legal_notice_page_url": "http://www.ticketstar.jp/legal",
        "legal_notice_page_url_mobile": "http://www.ticketstar.jp/legal",
        "mail_filter_domain_notice_template": u"予約受付完了メール等をメールでご案内します。「{domain}」からのメールを受信できるよう、お申し込み前にドメイン指定の設定を必ずお願いいたします。",
        }, 
    {
        "_type": "standard", 
        "_organization": "VS", 
        "mobile_marker_color": "#F0F222", 
        "mobile_required_marker_color": "#ff0000", 
        "mobile_header_background_color": "#177047", 
        "operator_info_url": "http://www.ticketstar.jp", 
        "contact_url": "", 
        "contact_url_mobile": "", 
        "privacy_policy_page_url": "http://www.ticketstar.jp/privacy", 
        "privacy_policy_page_url_mobile": "http://www.ticketstar.jp/privacy", 
        "legal_notice_page_url": "http://www.ticketstar.jp/legal",
        "legal_notice_page_url_mobile": "http://www.ticketstar.jp/legal",
        "mail_filter_domain_notice_template": u"予約受付完了メール等をメールでご案内します。「{domain}」からのメールを受信できるよう、お申し込み前にドメイン指定の設定を必ずお願いいたします。",
        }, 
    {
        "_type": "standard", 
        "_organization": "vissel", 
        "mobile_marker_color": "#960020", 
        "mobile_required_marker_color": "#ff0000", 
        "mobile_header_background_color": "#960020", 
        "operator_info_url": "http://www.ticketstar.jp/corporate", 
        "contact_url": "mailto:vissel@tstar.jp", 
        "contact_url_mobile": "mailto:vissel@tstar.jp", 
        "privacy_policy_page_url": "http://www.ticketstar.jp/privacy", 
        "privacy_policy_page_url_mobile": "http://www.ticketstar.jp/privacy", 
        "legal_notice_page_url": "http://www.ticketstar.jp/legal",
        "legal_notice_page_url_mobile": "http://www.ticketstar.jp/legal",
        "mail_filter_domain_notice_template": u"予約受付完了メール等をメールでご案内します。「{domain}」からのメールを受信できるよう、お申し込み前にドメイン指定の設定を必ずお願いいたします。",
        }, 
    {
        "_type": "standard", 
        "_organization": "VV", 
        "mobile_marker_color": "#ea9f27", 
        "operator_info_url": "http://www.ticketstar.jp", 
        "mobile_required_marker_color": "#ff0000", 
        "mobile_header_background_color": "#09355f", 
        "contact_url": "", 
        "contact_url_mobile": "", 
        "privacy_policy_page_url": "http://www.ticketstar.jp/privacy", 
        "privacy_policy_page_url_mobile": "http://www.ticketstar.jp/privacy", 
        "legal_notice_page_url": "http://www.ticketstar.jp/legal",
        "legal_notice_page_url_mobile": "http://www.ticketstar.jp/legal",
        "mail_filter_domain_notice_template": u"予約受付完了メール等をメールでご案内します。「{domain}」からのメールを受信できるよう、お申し込み前にドメイン指定の設定を必ずお願いいたします。",
        }, 
    {
        "_type": "standard", 
        "_organization": "eagles", 
        "mobile_marker_color": "#a01e23", 
        "mobile_required_marker_color": "#ff0000", 
        "mobile_header_background_color": "#a01e23", 
        "operator_info_url": "http://www.ticketstar.jp", 
        "contact_url": "", 
        "contact_url_mobile": "", 
        "privacy_policy_page_url": "http://privacy.rakuten.co.jp/", 
        "privacy_policy_page_url_mobile": "http://privacy.rakuten.co.jp/", 
        "legal_notice_page_url": "http://eagles.tstar.jp/legal",
        "legal_notice_page_url_mobile": "http://eagles.tstar.jp/legal",
        "mail_filter_domain_notice_template": u"予約受付完了メール等をメールでご案内します。「{domain}」からのメールを受信できるよう、お申し込み前にドメイン指定の設定を必ずお願いいたします。",
        }, 
    {
        "_type": "standard", 
        "_organization": "CR", 
        "mobile_marker_color": "#580d9a", 
        "mobile_required_marker_color": "#ff0000", 
        "mobile_header_background_color": "#9b63c0", 
        "operator_info_url": "http://www.ticketstar.jp/corporate", 
        "contact_url": "mailto:tokyo-cr@tstar.jp", 
        "contact_url_mobile": "mailto:tokyo-cr@tstar.jp", 
        "privacy_policy_page_url": "http://privacy.rakuten.co.jp/", 
        "privacy_policy_page_url_mobile": "http://privacy.rakuten.co.jp/", 
        "legal_notice_page_url": "http://www.ticketstar.jp/legal",
        "legal_notice_page_url_mobile": "http://www.ticketstar.jp/legal",
        "mail_filter_domain_notice_template": u"予約受付完了メール等をメールでご案内します。「{domain}」からのメールを受信できるよう、お申し込み前にドメイン指定の設定を必ずお願いいたします。",
        }, 
    {
        "_type": "standard", 
        "_organization": "KE", 
        "mobile_marker_color": "#FEBF00", 
        "mobile_header_background_color": "#DD1F55", 
        "mobile_required_marker_color": "#ff0000",
        "operator_info_url": "http://www.ticketstar.jp/corporate", 
        "contact_url": "mailto:tokyo-cr@tstar.jp", 
        "contact_url_mobile": "mailto:tokyo-cr@tstar.jp", 
        "privacy_policy_page_url": "http://www.ticketstar.jp/privacy", 
        "privacy_policy_page_url_mobile": "http://www.ticketstar.jp/privacy", 
        "legal_notice_page_url": "http://www.ticketstar.jp/legal",
        "legal_notice_page_url_mobile": "http://www.ticketstar.jp/legal",
        "mail_filter_domain_notice_template": u"予約受付完了メール等をメールでご案内します。「{domain}」からのメールを受信できるよう、お申し込み前にドメイン指定の設定を必ずお願いいたします。",
        }, 
    {
        "_type": "standard", 
        "_organization": "89ers", 
        "mobile_marker_color": "#ffb700", 
        "mobile_required_marker_color": "#ff0000", 
        "mobile_header_background_color": "#ffb700", 
        "operator_info_url": "http://www.ticketstar.jp/corporate", 
        "contact_url": "mailto:89ers@tstar.jp", 
        "contact_url_mobile": "mailto:89ers@tstar.jp", 
        "privacy_policy_page_url": "http://www.ticketstar.jp/privacy", 
        "privacy_policy_page_url_mobile": "http://www.ticketstar.jp/privacy", 
        "legal_notice_page_url": "http://www.ticketstar.jp/legal",
        "legal_notice_page_url_mobile": "http://www.ticketstar.jp/legal",
        "mail_filter_domain_notice_template": u"予約受付完了メール等をメールでご案内します。「{domain}」からのメールを受信できるよう、お申し込み前にドメイン指定の設定を必ずお願いいたします。",
        }, 
    {
        "_type": "standard", 
        "_organization": "OG", 
        "mobile_marker_color": "#F0F222", 
        "mobile_required_marker_color": "#ff0000", 
        "mobile_header_background_color": "#177047", 
        "operator_info_url": "http://www.ticketstar.jp", 
        "contact_url": "", 
        "contact_url_mobile": "", 
        "privacy_policy_page_url": "http://www.ticketstar.jp/privacy", 
        "privacy_policy_page_url_mobile": "http://www.ticketstar.jp/privacy", 
        "legal_notice_page_url": "http://www.ticketstar.jp/legal",
        "legal_notice_page_url_mobile": "http://www.ticketstar.jp/legal",
        "mail_filter_domain_notice_template": u"予約受付完了メール等をメールでご案内します。「{domain}」からのメールを受信できるよう、お申し込み前にドメイン指定の設定を必ずお願いいたします。",
        }, 
    {
        "_type": "standard", 
        "_organization": "KH", 
        "mobile_marker_color": "#003366", 
        "mobile_required_marker_color": "#ff0000", 
        "mobile_header_background_color": "#41A5D7", 
        "operator_info_url": "http://www.ticketstar.jp", 
        "contact_url": "", 
        "contact_url_mobile": "", 
        "privacy_policy_page_url": "http://www.ticketstar.jp/privacy", 
        "privacy_policy_page_url_mobile": "http://www.ticketstar.jp/privacy", 
        "legal_notice_page_url": "http://www.ticketstar.jp/legal/",
        "legal_notice_page_url_mobile": "http://www.ticketstar.jp/legal/",
        "mail_filter_domain_notice_template": u"予約受付完了メール等をメールでご案内します。「{domain}」からのメールを受信できるよう、お申し込み前にドメイン指定の設定を必ずお願いいたします。",
        }, 
    {
        "_type": "standard", 
        "_organization": "lakestars", 
        "mobile_marker_color": "#f39700", 
        "mobile_required_marker_color": "#ff0000", 
        "mobile_header_background_color": "#f39700", 
        "operator_info_url": "http://www.ticketstar.jp/corporate", 
        "contact_url": "mailto:lakestars@tstar.jp", 
        "contact_url_mobile": "mailto:lakestars@tstar.jp", 
        "privacy_policy_page_url": "http://www.ticketstar.jp/privacy", 
        "privacy_policy_page_url_mobile": "http://www.ticketstar.jp/privacy", 
        "legal_notice_page_url": "http://www.ticketstar.jp/legal",
        "legal_notice_page_url_mobile": "http://www.ticketstar.jp/legal",
        "mail_filter_domain_notice_template": u"予約受付完了メール等をメールでご案内します。「{domain}」からのメールを受信できるよう、お申し込み前にドメイン指定の設定を必ずお願いいたします。",
        }, 
    {
        "_type": "standard", 
        "_organization": "QA", 
        "mobile_marker_color": "#a01e23", 
        "mobile_required_marker_color": "#ff0000", 
        "mobile_header_background_color": "#a01e23", 
        "operator_info_url": "http://www.ticketstar.jp", 
        "contact_url": "",
        "contact_url_mobile": "",
        "privacy_policy_page_url": "http://privacy.rakuten.co.jp/", 
        "privacy_policy_page_url_mobile": "http://privacy.rakuten.co.jp/", 
        "legal_notice_page_url": "http://eagles.tstar.jp/legal",
        "legal_notice_page_url_mobile": "http://eagles.tstar.jp/legal",
        "mail_filter_domain_notice_template": u"予約受付完了メール等をメールでご案内します。「{domain}」からのメールを受信できるよう、お申し込み前にドメイン指定の設定を必ずお願いいたします。",
        }, 
    {
        "_type": "standard", 
        "_organization": "oxtv", 
        "mobile_marker_color": "#120086", 
        "mobile_required_marker_color": "#ff0000", 
        "mobile_header_background_color": "#120086", 
        "operator_info_url": "http://www.ticketstar.jp/corporate", 
        "contact_url": "mailto:oxtv@tstar.jp", 
        "contact_url_mobile": "mailto:oxtv@tstar.jp", 
        "privacy_policy_page_url": "http://www.ticketstar.jp/privacy", 
        "privacy_policy_page_url_mobile": "http://www.ticketstar.jp/privacy", 
        "legal_notice_page_url": "http://www.ticketstar.jp/legal",
        "legal_notice_page_url_mobile": "http://www.ticketstar.jp/legal",
        "mail_filter_domain_notice_template": u"予約受付完了メール等をメールでご案内します。「{domain}」からのメールを受信できるよう、お申し込み前にドメイン指定の設定を必ずお願いいたします。",
        }, 
    {
        "_type": "standard", 
        "_organization": "KT", 
        "mobile_marker_color": "#F0F222", 
        "mobile_required_marker_color": "#ff0000", 
        "mobile_header_background_color": "#177047", 
        "operator_info_url": "http://www.ticketstar.jp", 
        "contact_url": "", 
        "contact_url_mobile": "", 
        "privacy_policy_page_url": "http://www.ticketstar.jp/privacy", 
        "privacy_policy_page_url_mobile": "http://www.ticketstar.jp/privacy", 
        "legal_notice_page_url": "http://www.ticketstar.jp/legal",
        "legal_notice_page_url_mobile": "http://www.ticketstar.jp/legal",
        "mail_filter_domain_notice_template": u"予約受付完了メール等をメールでご案内します。「{domain}」からのメールを受信できるよう、お申し込み前にドメイン指定の設定を必ずお願いいたします。",
        }, 
    {
        "_type": "standard", 
        "_organization": "SC", 
        "mobile_marker_color": "#FEBF00", 
        "mobile_header_background_color": "#1D2B62", 
        "mobile_required_marker_color": "#ff0000",
        "contact_url":"http://www.sound-c.co.jp/contact/",
        "privacy_policy_page_url_mobile":"http://www.sound-c.co.jp/privacy/",
        "legal_notice_page_url_mobile": "http://sc.tstar.jp/tokushoho.html",
        "mail_filter_domain_notice_template": u"予約受付完了メール等をメールでご案内します。「{domain}」からのメールを受信できるよう、お申し込み前にドメイン指定の設定を必ずお願いいたします。",
        "extra_footer_links": [
            {"text":u"利用規約", "url":"http://sc.tstar.jp/kiyaku.html"},
            {"text":u"ライブ・エンタテインメント約款", "url":"http://www.acpc.or.jp/concert/"}
            ],
        "extra_footer_links_mobile": [
            {"text":u"利用規約", "url":"http://sc.tstar.jp/kiyaku.html"},
            {"text":u"ライブ・エンタテインメント約款", "url":"http://www.acpc.or.jp/concert/"}
            ]
        }
    ]

def upgrade():
    op.create_table(
        'CartSetting',
        sa.Column('id', Identifier, primary_key=True),
        sa.Column('organization_id', Identifier, sa.ForeignKey('Organization.id')),
        sa.Column('name', sa.Unicode(128), nullable=False, default=u''),
        sa.Column('type', sa.Unicode(64), nullable=False, default=u''),
        sa.Column('performance_selector', sa.Unicode(128)),
        sa.Column('performance_selector_label1_override', sa.Unicode(128), nullable=True),
        sa.Column('performance_selector_label2_override', sa.Unicode(128), nullable=True),
        sa.Column('data', JSONEncodedDict(16384), nullable=False, default={}, server_default='{}'),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True)
        )
    op.add_column('OrganizationSetting', sa.Column('cart_setting_id', Identifier))
    op.create_foreign_key('OrganizationSetting_ibfk_2', 'OrganizationSetting', 'CartSetting', ['cart_setting_id'], ['id'], ondelete='CASCADE')
    op.add_column('EventSetting', sa.Column('cart_setting_id', Identifier))
    op.create_foreign_key('EventSetting_ibfk_2', 'EventSetting', 'CartSetting', ['cart_setting_id'], ['id'], ondelete='CASCADE')
    op.execute("""INSERT INTO CartSetting (type, data, organization_id, performance_selector) SELECT 'standard', CONCAT('{"_organization_setting_id":', OrganizationSetting.id, '}'), organization_id, performance_selector FROM OrganizationSetting JOIN Organization ON OrganizationSetting.organization_id=Organization.id AND Organization.deleted_at IS NULL WHERE OrganizationSetting.deleted_at IS NULL;""")
    for data in settings_list:
        data = data.copy()
        short_name = data.pop('_organization')
        type = data.pop('_type')
        event_id = data.pop('_event_id')
        op.execute(u"""INSERT INTO CartSetting (type, data, organization_id) VALUES ('%(type)s', '%(data)s', (SELECT id FROM Organization WHERE short_name='%(short_name)s'));""" % dict(
            type=type,
            data=json.dumps(data, ensure_ascii=False),
            short_name=short_name
            ))
        op.execute(u"""UPDATE EventSetting SET cart_setting_id=(SELECT id FROM CartSetting WHERE type='%(type)s') WHERE event_id=%(event_id)s;""" % dict(
            type=type,
            event_id=event_id
            ))
    op.execute("""INSERT INTO CartSetting (type, data, organization_id, performance_selector, performance_selector_label1_override, performance_selector_label2_override) SELECT 'standard', CONCAT('{"_event_setting_id":', EventSetting.id, '}'), Event.organization_id, performance_selector, performance_selector_label1_override, performance_selector_label2_override FROM EventSetting JOIN Event ON EventSetting.event_id=Event.id AND Event.deleted_at IS NULL JOIN Organization ON Event.organization_id=Organization.id AND Organization.deleted_at IS NULL WHERE EventSetting.deleted_at IS NULL AND (performance_selector IS NOT NULL OR performance_selector_label1_override IS NOT NULL OR performance_selector_label2_override IS NOT NULL);""")
    op.execute("""UPDATE OrganizationSetting JOIN CartSetting ON CartSetting.data=CONCAT('{"_organization_setting_id":', OrganizationSetting.id, '}') SET cart_setting_id=CartSetting.id;""")
    op.execute("""UPDATE EventSetting JOIN CartSetting ON CartSetting.data=CONCAT('{"_event_setting_id":', EventSetting.id, '}') SET cart_setting_id=CartSetting.id;""")
    op.execute("""UPDATE EventSetting JOIN Event ON EventSetting.event_id=Event.id JOIN Organization ON Organization.id=Event.organization_id JOIN OrganizationSetting ON Organization.id=OrganizationSetting.organization_id SET EventSetting.cart_setting_id=OrganizationSetting.cart_setting_id WHERE EventSetting.cart_setting_id IS NULL;""")
    for data in standard_settings_list:
        data = data.copy()
        short_name = data.pop('_organization')
        type = data.pop('_type')
        op.execute(u"""UPDATE CartSetting SET data=REPLACE(data, '"_organization_setting_id"', CONCAT('%(additional_data)s', ', "_organization_setting_id"')) WHERE CartSetting.data=CONCAT('{"_organization_setting_id":', (SELECT OrganizationSetting.id FROM Organization JOIN OrganizationSetting ON Organization.id=OrganizationSetting.organization_id WHERE short_name='%(short_name)s'), '}');""" % dict(
            type=type,
            additional_data=re.sub(ur"^\{\s*|\s*\}$", "", json.dumps(data, ensure_ascii=False)),
            short_name=short_name
            ))
        op.execute(u"""UPDATE CartSetting JOIN EventSetting ON EventSetting.cart_setting_id=CartSetting.id JOIN Event ON EventSetting.event_id=Event.id JOIN Organization ON Event.organization_id=Organization.id SET data=REPLACE(data, '"_event_setting_id"', CONCAT('%(additional_data)s', ', "_event_setting_id"')) WHERE Organization.short_name='%(short_name)s';""" % dict(
            type=type,
            additional_data=re.sub(ur"^\{\s*|\s*\}$", "", json.dumps(data, ensure_ascii=False)),
            short_name=short_name
            ))
    op.drop_constraint('cart_session_id', 'Cart', type_='unique')
    op.add_column('multicheckout_request_card', sa.Column('card_brand', sa.Unicode(20)))
    op.execute("""ALTER TABLE Cart ADD COLUMN cart_setting_id BIGINT NOT NULL, MODIFY COLUMN cart_session_id VARBINARY(72) DEFAULT '', ADD COLUMN user_agent VARBINARY(200) DEFAULT '', ADD COLUMN membership_id BIGINT, ADD CONSTRAINT Cart_ibfk_9 FOREIGN KEY Cart_ibfk_9 (membership_id) REFERENCES Membership (id);""")
    op.execute("""ALTER TABLE `Order` ADD COLUMN cart_setting_id BIGINT NOT NULL, ADD COLUMN membership_id BIGINT, ADD CONSTRAINT Order_ibfk_9 FOREIGN KEY Order_ibfk_9 (membership_id) REFERENCES Membership (id);""")
    op.add_column('LotEntry', sa.Column('membership_id', Identifier, sa.ForeignKey('Membership.id', name='LotEntry_ibfk_9')))
    op.execute("""UPDATE LotEntry JOIN MemberGroup ON LotEntry.membergroup_id=MemberGroup.id SET LotEntry.membership_id=MemberGroup.membership_id WHERE LotEntry.membership_id IS NULL;""")
    op.execute("""UPDATE LotEntry JOIN UserCredential ON LotEntry.user_id=UserCredential.user_id SET LotEntry.membership_id=UserCredential.membership_id WHERE LotEntry.membership_id IS NULL;""")
    op.execute("""UPDATE Cart JOIN Performance ON Cart.performance_id=Performance.id JOIN EventSetting ON EventSetting.event_id=Performance.event_id SET Cart.cart_setting_id=EventSetting.cart_setting_id;""")
    op.execute("""UPDATE `Order` JOIN Performance ON `Order`.performance_id=Performance.id JOIN EventSetting ON EventSetting.event_id=Performance.event_id SET `Order`.cart_setting_id=EventSetting.cart_setting_id;""")
    op.execute("""UPDATE `Order` JOIN `UserCredential` ON `Order`.user_id=`UserCredential`.user_id SET `Order`.membership_id=`UserCredential`.membership_id WHERE `Order`.membership_id IS NULL;""")
    op.execute("""UPDATE `Order` JOIN `Organization` ON `Order`.organization_id=`Organization`.id JOIN `Membership` ON `Order`.organization_id=`Membership`.organization_id AND `Membership`.name=`Organization`.short_name SET `Order`.membership_id=`Membership`.id WHERE `Order`.membership_id IS NULL;""")

def downgrade():
    op.drop_constraint('LotEntry_ibfk_9', 'LotEntry', type_='foreignkey')
    op.drop_constraint('Order_ibfk_9', 'Order', type_='foreignkey')
    op.drop_constraint('Cart_ibfk_9', 'Cart', type_='foreignkey')
    op.execute("""ALTER TABLE `Order` DROP COLUMN cart_setting_id, DROP COLUMN membership_id;""")
    op.execute("""ALTER TABLE Cart DROP COLUMN cart_setting_id, MODIFY COLUMN cart_session_id VARCHAR(255) DEFAULT NULL, DROP COLUMN user_agent, DROP COLUMN membership_id;""")
    op.drop_column('LotEntry', 'membership_id')
    op.drop_column('multicheckout_request_card', 'card_brand')
    op.execute("""UPDATE Cart SET cart_session_id=NULL;""")
    op.create_index('cart_session_id', 'Cart', ['cart_session_id'], unique=True)
    op.drop_constraint('EventSetting_ibfk_2', 'EventSetting', type_='foreignkey')
    op.drop_column('EventSetting', 'cart_setting_id')
    op.drop_constraint('OrganizationSetting_ibfk_2', 'OrganizationSetting', type_='foreignkey')
    op.drop_column('OrganizationSetting', 'cart_setting_id')
    op.drop_table('CartSetting')
