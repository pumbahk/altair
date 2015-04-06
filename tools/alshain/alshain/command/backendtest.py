#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""altair backend巡回テストscript
"""
import sys
import time
import random
import string
import datetime
import argparse
import selenium.webdriver.common.proxy
from selenium.webdriver.common.keys import Keys
from pywad.part import Part
from pywad.utils import get_driver
from pywad.runner import Runner
from pywad.decorator import url_match
from pit import Pit


class BackendOperationError(Exception):
    pass


def get_code(num):
    CANUSE_CHARS = list(string.uppercase)
    random.shuffle(CANUSE_CHARS)
    return unicode(''.join(CANUSE_CHARS[:num]))


class BackendLogin(Part):
    """ログインページ
    """
    @url_match('/login')
    def is_target(self, browser, status):
        return True

    def run(self, browser, status):
        entries = browser.find_elements_by_css_selector('input')
        backendtest = Pit.get('backendtest',
                              {'require': {'username': '',
                                           'password': '',
                                           }})

        name_value = {
            'text': backendtest['username'],
            'password': backendtest['password'],
            }

        for entry in entries:
            type_ = entry.get_attribute('type')
            try:
                value = name_value[type_]
            except KeyError:
                pass
            else:
                entry.send_keys(value)

        for entry in entries:
            type_ = entry.get_attribute('type')
            if type_ == 'submit':
                entry.submit()
                break
        else:
            raise BackendOperationError()


class Events(Part):
    """イベント一覧
    """
    def __init__(self, *args, **kwds):
        super(type(self), self).__init__(*args, **kwds)
        self.created_at = None

    @url_match('/events/$')
    def is_target(self, browser, status):
        return True

    def run(self, browser, status):
        if self.created_at:
            pass
        else:
            self.jump_create_event(browser)

    def jump_create_event(self, browser):
        """
        """
        btns = browser.find_elements_by_class_name('btn')
        for btn in btns:
            if btn.text == u'新規イベント':
                btn.click()
                self.created_at = datetime.datetime.now()
                break
        else:
            raise BackendOperationError()


class EventsNew(Part):
    """イベント作成ページ
    """

    def __init__(self, title='TEST'):
        self.title = title

    @url_match('/events/new$')
    def is_target(self, browser, status):
        return True

    def run(self, browser, status):
        id_value = {
            'title': self.title,
            'abbreviated_title': u'TEST',
            'code': get_code(7),
            'display_order': '-100',
        }

        for id_, value in id_value.items():
            tag = browser.find_element_by_id(id_)
            tag.send_keys(Keys.BACK_SPACE * 10)
            tag.send_keys(value)

        entries = browser.find_elements_by_css_selector('input')
        for entry in entries:
            type_ = entry.get_attribute('type')
            value = entry.get_attribute('value')
            if type_ == 'submit' and value == u'登録':
                entry.submit()
                break
        else:
            raise BackendOperationError()


class StockTypeCreator(Part):
    """イベント詳細ページ 席種作成
    """

    def __init__(self, *args, **kwds):
        super(type(self), self).__init__(*args, **kwds)
        self.stock_type_created_at = None

    @url_match('/events/show/(?P<event_id>\d+)$')
    def is_target(self, browser, status):
        return not self.stock_type_created_at

    def run(self, browser, status):
        self.create_stock_type(browser, status)

    def create_stock_type(self, browser, status):
        stock_types = browser.find_element_by_id('stock_types')
        btn_group = stock_types.find_element_by_class_name('btn-group')
        atags = btn_group.find_elements_by_tag_name('a')
        for tag in atags:
            if tag.text == u'新規':
                tag.click()
                while True:
                    self.operate_modal_create_stock_type(browser, status)
                    if self.could_save_stock_type(browser, status):
                        self.stock_type_created_at = datetime.datetime.now()
                        break
                break
        else:
            raise BackendOperationError()

    def operate_modal_create_stock_type(self, browser, status):
        modal = browser.find_element_by_id('modal-stock_type')
        id_value = {
            'name': u'TEST',
            'quantity_only': True,
            }

        for id_, value in id_value.items():
            tag = modal.find_element_by_id(id_)
            if value in (True, False):
                if value:
                    tag.click()
            else:
                tag.send_keys(value)

        atags = modal.find_elements_by_tag_name('input')
        for tag in atags:
            if tag.get_attribute('value') == u'保存':
                tag.click()
                break
        else:
            raise BackendOperationError()

    def could_save_stock_type(self, browser, status):
        time.sleep(1)
        messages = browser.find_elements_by_class_name('alert-heading')
        for message in messages:
            if message.text == u'席種を保存しました':
                return True
        return False


class _TicketCreator(Part):
    """イベント詳細ページ 券面 作成
    """

    def __init__(self, *args, **kwds):
        super(type(self), self).__init__(*args, **kwds)
        self.created_at = None

    @url_match('/events/show/(?P<event_id>\d+)$')
    def is_target(self, browser, status):
        return not self.created_at

    def run(self, browser, status):
        self.create_stock_type(browser, status)


class BreadCrumbMixin:
    def get_bread_crumb(self, browser, status):
        breadcrumb = browser.find_elements_by_class_name('breadcrumb')[0]
        atags = breadcrumb.find_elements_by_tag_name('a')
        return list(atags)

    def jump_events_show_page(self, browser, status):
        breadcrumb = browser.find_elements_by_class_name('breadcrumb')[0]
        atags = breadcrumb.find_elements_by_tag_name('a')
        if len(atags) >= 2:
            atags[1].click()
        else:
            raise BackendOperationError()


class ReturnEventPageFromTicketPage(Part, BreadCrumbMixin):
    @url_match('/events/tickets/event/(?P<event_id>\d+)/$')
    def is_target(self, browser, status):
        return True

    def run(self, *args, **kwds):
        self.jump_events_show_page(*args, **kwds)


class TicketCreator(Part):
    """イベント詳細ページから 券面関連 作成
    """

    def __init__(self, *args, **kwds):
        super(type(self), self).__init__(*args, **kwds)
        self.ticket_created_at = None
        self.ticket_bundle_created_at = None

    @url_match('/events/show/(?P<event_id>\d+)$')
    def is_target(self, browser, status):
        return not (self.ticket_created_at and self.ticket_bundle_created_at)

    def run(self, browser, status):
        self.jump_tickets_page(browser, status)
        if not self.ticket_created_at:
            self.create_ticket(browser, status)

        if not self.ticket_bundle_created_at:
            self.create_ticket_bundle(browser, status)

    def jump_tickets_page(self, browser, status):
        tags = browser.find_elements_by_css_selector('a.btn')
        for tag in tags:
            if tag.text == u'券面':
                tag.click()
                time.sleep(1)
                break
        else:
            raise BackendOperationError()

    def create_ticket(self, browser, status):
        """券面作成
        """
        tags = browser.find_elements_by_css_selector('form#tickets div.row-fluid.well div.btn-group a')
        for tag in tags:
            if u'チケット券面追加' in tag.text:
                tag.click()
                time.sleep(1)
                break
        else:
            raise BackendOperationError()

        self.operate_modal_create_ticket(browser, status)

    def operate_modal_create_ticket(self, browser, status):
        """券面作成のモーダル操作
        """
        modal = browser.find_element_by_id('AjaxModal')
        name = modal.find_element_by_id('name')
        for ii in range(50):
            name.send_keys(Keys.BACK_SPACE)
        name.send_keys(u'TEST')
        tags = modal.find_elements_by_tag_name('input')
        for tag in tags:
            if tag.get_attribute('value') == u'登録' and\
               tag.get_attribute('type') == 'submit':
                tag.click()
                break
        else:
            raise BackendOperationError()

        if not self.could_register_ticket(browser, status):
            raise BackendOperationError()

    def could_register_ticket(self, browser, status):
        time.sleep(1)
        messages = browser.find_elements_by_class_name('alert-heading')
        for message in messages:
            if message.text == u'チケットが登録されました':
                self.ticket_created_at = datetime.datetime.now()
                return True
        return False

    def create_ticket_bundle(self, browser, status):
        """券面構成作成
        """
        tags = browser.find_elements_by_css_selector('form#ticket-bundle div.row-fluid.well div.btn-group a')
        for tag in tags:
            if u'を追加' in tag.text:
                tag.click()
                time.sleep(1)
                break
        else:
            raise BackendOperationError()

        self.operate_modal_create_ticket_bundle(browser, status)

    def operate_modal_create_ticket_bundle(self, browser, status):
        """券面構成作成のモーダル操作
        """
        modal = browser.find_element_by_id('AjaxModal')
        name = modal.find_element_by_id('name')
        name.send_keys(Keys.BACK_SPACE * 50)
        name.send_keys(u'TEST')

        option = modal.find_element_by_tag_name('option')
        option.click()

        tags = modal.find_elements_by_tag_name('input')
        for tag in tags:
            if tag.get_attribute('value') == u'登録' and\
               tag.get_attribute('type') == 'submit':
                tag.click()
                break
        else:
            raise BackendOperationError()

        if not self.could_register_ticket_bundle(browser, status):
            raise BackendOperationError()

    def could_register_ticket_bundle(self, browser, status):
        time.sleep(1)
        messages = browser.find_elements_by_class_name('alert-heading')
        for message in messages:
            if message.text == u'チケット券面構成(TicketBundle)が登録されました':
                self.ticket_bundle_created_at = datetime.datetime.now()
                return True
        return False


class SalesSegmentGroupCreator(Part):
    """イベント詳細ページ 販売区分グループ作成
    """

    def __init__(self, *args, **kwds):
        super(type(self), self).__init__(*args, **kwds)
        self.created_at = None

    @url_match('/events/show/(?P<event_id>\d+)$')
    def is_target(self, browser, status):
        return not self.created_at

    def run(self, browser, status):
        self.create_sales_segment_group(browser, status)

    def create_sales_segment_group(self, browser, status):
        atags = browser.find_elements_by_css_selector(
            '#sales_segment_groups div form div a')
        for atag in atags:
            if atag.text == u'新規':
                atag.click()
                break
        else:
            raise BackendOperationError()

        self.operate_modal_create_sales_segment_group(browser, status)
        if not self.could_register_sales_segment_group(browser, status):
            raise BackendOperationError()

    def operate_modal_create_sales_segment_group(self, browser, status):
        modal = browser.find_element_by_id('modal-sales_segment_group')

        name = modal.find_element_by_id('name')
        name.send_keys(Keys.BACK_SPACE * 50)
        name.send_keys(u'TEST')

        # calender control
        icalenders = modal.find_elements_by_css_selector('i.icon-calendar')
        if len(icalenders) < 2:
            raise BackendOperationError()
        start_at_calender = Datepicker(icalenders[0])
        end_at_calender = Datepicker(icalenders[1])
        start_at_calender.click()
        start_at_calender.prev()
        start_at_calender.select(10)

        end_at_calender.click()
        end_at_calender.next()
        end_at_calender.select(20)

        atags = modal.find_elements_by_tag_name('a')

        browser.maximize_window()  # <=_(-_-;) Last resort
        for atag in atags:
            if atag.text == u'保存':
                atag.click()
                break
        else:
            raise BackendOperationError()

    def could_register_sales_segment_group(self, browser, status):
        msg = u'販売区分グループを保存しました'

        time.sleep(1)
        alerts = browser.find_elements_by_class_name('alert-heading')
        for alert in alerts:
            if alert.text == msg:
                self.created_at = datetime.datetime.now()
                return True
        return False


class JumpSalesSegmentGroupShowPage(Part):
    """イベント詳細ページ 販売区分グループ詳細ページへ移動
    """
    def __init__(self, *args, **kwds):
        super(type(self), self).__init__(*args, **kwds)
        self.max_count = 1
        self.count = 0

    @url_match('/events/show/(?P<event_id>\d+)$')
    def is_target(self, browser, status):
        return self.count < self.max_count

    def run(self, *args, **kwds):
        self.jump_sales_segment_group_show_page(*args, **kwds)

    def jump_sales_segment_group_show_page(self, browser, status):
        tag = browser.find_element_by_css_selector('div#sales_segment_groups')
        table = tag.find_element_by_tag_name('table')
        atags = table.find_elements_by_tag_name('a')
        if len(atags) >= 1:
            atags[-1].click()  # last
            self.count += 1
        else:
            raise BackendOperationError()


class Datepicker(object):
    def __init__(self, switch):
        self._switch = switch
        self._core = None

    def click(self):
        self._switch.click()
        time.sleep(1)
        tags = self._switch.parent.find_elements_by_css_selector('div.datepicker')
        for tag in tags:
            if tag.is_displayed():
                self._core = tag
                break
        else:
            raise BackendOperationError()

    def prev(self):
        btn = self._core.find_element_by_class_name('prev')
        btn.click()
        time.sleep(1)

    def next(self):
        btn = self._core.find_element_by_class_name('next')
        btn.click()
        time.sleep(1)

    def select(self, num):
        tags = self._core.find_elements_by_class_name('day')
        for tag in tags:
            if tag.text == unicode(num):
                tag.click()
                break
        else:
            raise BackendOperationError()


class SalesSegmentGroupShowPageMixin(object):
    def get_btn_groups(self, browser, status):
        btn_groups = browser.find_elements_by_css_selector('div.btn-group')
        ssg_btn_group = btn_groups[0]
        lot_btn_group = btn_groups[1]
        pdmp_btn_group = btn_groups[2]
        mbg_btn_group = btn_groups[3]
        ss_btn_group = btn_groups[4]
        return {'ssg': ssg_btn_group,
                'lot': lot_btn_group,
                'pdmp': pdmp_btn_group,
                'mbg': mbg_btn_group,
                'ss': ss_btn_group,
                }


class SalesSegmentGroupEdit(Part, SalesSegmentGroupShowPageMixin):
    """販売区分グループ詳細ページ 販売区分グループ編集
    """
    def __init__(self, *args, **kwds):
        super(type(self), self).__init__(*args, **kwds)
        self.modified_at = None

    @url_match('/events/sales_segment_groups/show/(?P<event_id>\d+)$')
    def is_target(self, browser, status):
        return not self.modified_at

    def run(self, *args, **kwds):
        self.edit_sales_segment_group(*args, **kwds)

    def edit_sales_segment_group(self, browser, status):
        self.push_edit_button(browser, status)
        self.operate_modal_sales_segment_group(browser, status)
        if not self.could_register_sales_segment_group(browser, status):
            raise BackendOperationError()

    def push_edit_button(self, browser, status):
        btn_groups = self.get_btn_groups(browser, status)
        btn_group = btn_groups['ssg']
        btn = btn_group.find_element_by_css_selector('a.btn')
        btn.click()

    def operate_modal_sales_segment_group(self, browser, status):
        modal = browser.find_element_by_id('modal-sales_segment_group')

        public = modal.find_element_by_css_selector('input#public')
        public.click()

        browser.maximize_window()  # <=_(-_-;) Last resort
        atags = modal.find_elements_by_css_selector('a.btn')
        for tag in atags:
            if tag.text == u'保存':
                tag.click()
                break
        else:
            raise BackendOperationError()

    def could_register_sales_segment_group(self, browser, status):
        msg = u'販売区分グループを保存しました'

        time.sleep(1)
        alerts = browser.find_elements_by_class_name('alert-heading')
        for alert in alerts:
            if alert.text == msg:
                self.modified_at = datetime.datetime.now()
                return True
        return False


class PDMPCreator(Part, SalesSegmentGroupShowPageMixin, BreadCrumbMixin):
    """販売区分グループ詳細ページ PDMP作成
    """
    def __init__(self, *args, **kwds):
        super(type(self), self).__init__(*args, **kwds)
        self.created_at = None

    @url_match('/events/sales_segment_groups/show/(?P<event_id>\d+)$')
    def is_target(self, browser, status):
        return not self.created_at

    def run(self, *args, **kwds):
        self.create_pdmp(*args, **kwds)
        self.jump_events_show_page(*args, **kwds)

    def create_pdmp(self, browser, status):
        self.push_add_button(browser, status)
        self.edit_pdmp_page(browser, status)
        if not self.could_saved(browser, status):
            raise BackendOperationError()

    def push_add_button(self, browser, status):
        btn_groups = self.get_btn_groups(browser, status)
        btn_group = btn_groups['pdmp']
        btns = btn_group.find_elements_by_css_selector('a.btn')
        for btn in btns:
            if u'引取方法を追加' in btn.text:
                btn.click()
                break
        else:
            raise BackendOperationError()

    def edit_pdmp_page(self, browser, status):
        method = browser.find_element_by_css_selector('#payment_method_id')
        options = method.find_elements_by_tag_name('option')
        for option in options:
            if u'インナー' in option.text:
                option.click()
                break
            elif u'窓口' in option.text:
                option.click()
                break
        else:
            raise BackendOperationError()

        method = browser.find_element_by_css_selector('#delivery_method_id')
        options = method.find_elements_by_tag_name('option')
        for option in options:
            if u'インナー' in option.text:
                option.click()
                break
            elif u'窓口' in option.text:
                option.click()
                break
        else:
            raise BackendOperationError()

        public = browser.find_element_by_css_selector('#public')
        public.click()

        btns = browser.find_elements_by_css_selector('input.btn')
        for btn in btns:
            if btn.get_attribute('value') == u'保存':
                btn.click()
                break
        else:
            raise BackendOperationError()

    def could_saved(self, browser, status):
        msg = u'決済・引取方法を登録しました'

        time.sleep(1)
        alerts = browser.find_elements_by_class_name('alert-heading')
        for alert in alerts:
            if msg in alert.text:
                self.created_at = datetime.datetime.now()
                return True
        return False


class PerformanceCreator(Part):
    """イベント詳細ページ Performance作成
    """

    def __init__(self, name='TEST', *args, **kwds):
        self.name = name
        self.created_at = None
        super(type(self), self).__init__(*args, **kwds)

    @url_match('/events/show/(?P<event_id>\d+)$')
    def is_target(self, browser, status):
        return not self.created_at

    def run(self, *args, **kwds):
        self.create_performance(*args, **kwds)

    def create_performance(self, browser, status):
        self.push_create_button(browser, status)
        self.edit_performance_page(browser, status)
        if not self.could_saved(browser, status):
            raise BackendOperationError()

    def push_create_button(self, browser, status):
        browser.execute_script('window.scrollTo(0, 1000)')
        href = u'/events/performances/new'
        new_text = u'新規'
        time.sleep(0.5)

        btns = browser.find_elements_by_css_selector('a.btn')
        for btn in btns:
            if new_text in btn.text and href in btn.get_attribute('href'):
                btn.click()
                break
        else:
            raise BackendOperationError()

    def edit_performance_page(self, browser, status):
        name_value = {u'name': self.name,
                      u'code': get_code(12),
                      }

        for name, value in name_value.items():
            tag = browser.find_element_by_id(name)
            tag.send_keys(Keys.BACK_SPACE * 50)
            tag.send_keys(value)

        self._input_start_on(browser, status)

        btns = browser.find_elements_by_css_selector('input.btn')
        for btn in btns:
            if u'submit' in btn.get_attribute('type') and u'登録' in btn.get_attribute('value'):
                btn.click()
                break
        else:
            raise BackendOperationError()

    def _input_start_on(self, browser, status):
        # calender control
        form = browser.find_element_by_id('main-container')
        icalenders = form.find_elements_by_css_selector('i.icon-calendar')
        if len(icalenders) < 2:
            raise BackendOperationError()
        start_on_calender = Datepicker(icalenders[1])
        start_on_calender.click()
        start_on_calender.next()
        start_on_calender.next()
        start_on_calender.next()
        start_on_calender.select(20)

    def could_saved(self, browser, status):
        msg = u'保存しました'

        time.sleep(1)
        alerts = browser.find_elements_by_class_name('alert-heading')
        for alert in alerts:
            if msg in alert.text:
                self.created_at = datetime.datetime.now()
                return True
        return False


class PerformanceDetailPage(Part):
    @url_match('/events/performances/show/(?P<performance_id>\d+)$')
    def is_target(self, browser, status):
        return True

    def run(self, browser, status):
        tab = browser.find_element_by_id('seat-allocation-tab')
        tab = tab.find_element_by_css_selector('a')
        tab.click()


class SeatAllocatorr(Part):
    """イベント詳細ページ Performance作成
    """

    def __init__(self, *args, **kwds):
        self.created_at = None
        super(type(self), self).__init__(*args, **kwds)

    @url_match('/events/performances/show/(?P<performance_id>\d+)/seat-allocation$')
    def is_target(self, browser, status):
        return True

    def run(self, *args, **kwds):
        if not self.created_at:
            self.allocate_seats(*args, **kwds)
        self.jump_product_page(*args, **kwds)

    def jump_product_page(self, browser, status):
        tab = browser.find_element_by_id('product-tab')
        tab = tab.find_element_by_css_selector('a')
        tab.click()

    def allocate_seats(self, browser, status):
        btn = browser.find_element_by_css_selector('a.btn-init-load')
        btn.click()

        time.sleep(3)

        span = list(browser.find_elements_by_css_selector('span.swatch'))[1]
        span.click()
        strnum = str(random.randint(100, 1000))

        script_ = "venueEditorRoot.venueeditor('model').stocks.each(function (stock){ stock.set('assigned', "+strnum+")});"
        browser.execute_script(script_)

        # spans = browser.find_elements_by_css_selector('span.editable')
        # span = spans[3] # (--;)
        # span.click()
        # time.sleep(1)

        # input_ = browser.find_element_by_css_selector('input.editable')
        # input_.click()
        # input_.send_keys('1000')
        # input_.send_keys(Keys.ENTER)

        btns = browser.find_elements_by_css_selector('a.btn.btn-primary')
        for btn in btns:
            if u'save' == btn.get_attribute('name'):
                btn.click()
                break
            else:
                raise BackendOperationError()

        time.sleep(3)
        self.created_at = datetime.datetime.now()


class ProductCreator(Part, BreadCrumbMixin):
    """商品作成page
    """

    def __init__(self, *args, **kwds):
        self.created_at = None
        super(type(self), self).__init__(*args, **kwds)

    @url_match('/events/performances/show/(?P<performance_id>\d+)/product\#.*$')
    def is_target(self, browser, status):
        return True

    def run(self, *args, **kwds):
        if not self.created_at:
            self.create_product(*args, **kwds)
        self.jump_performance_list_page(*args, **kwds)

    def jump_performance_list_page(self, browser, status):
        breadcrumb = self.get_bread_crumb(browser, status)
        link = breadcrumb[2]  # パフォーマンス一覧
        link.click()

    def create_product(self, browser, status):
        script_ = 'new_product(get_selected_sales_segment_id())'
        browser.execute_script(script_)

        input_ = browser.find_element_by_id('price')
        input_.send_keys('1')

        script_ = "$('#modal-product').find('form').submit()"
        browser.execute_script(script_)


class PerformancePublicChanger(Part):
    @url_match('/events/performances/(?P<event_id>\d+)$')
    def is_target(self, browser, status):
        return True

    def run(self, browser, status):
        while True:
            btn = browser.find_element_by_css_selector('.btn.btn-warning.btn-mini')
            if btn:
                btn.click()
                time.sleep(1)
                btns = browser.find_elements_by_css_selector('.btn.btn-danger')
                for btn in btns:
                    if 'delete' != btn.get_attribute('id'):
                        btn.click()
                        break
                time.sleep(3)
            else:
                break

        breadcrumb = self.get_bread_crumb(browser, status)
        link = breadcrumb[1]  # イベントページ
        link.click()


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('url', nargs='?', default='https://backend.stg.altr.jp')
    parser.add_argument('--event', default='TEST')
    parser.add_argument('--performance', default='TEST')
    parser.add_argument('--driver', default='firefox')
    parser.add_argument('--proxy', default=None)
    parser.add_argument('--local', default=False, action='store_true')
    opts = parser.parse_args(argv)

    url = opts.url

    basic_auth_pair = ''
    if 'stg2' in url or 'dev' in url:
        backendtest = Pit.get('backendtest',
                              {'require': {'basic_username': '',
                                           'basic_password': '',
                                           }})
        basic_username = backendtest['basic_username']
        basic_password = backendtest['basic_password']
        if basic_username and basic_password:
            basic_auth_pair = '{}:{}@'.format(basic_username, basic_password)
    url = url.replace('://', '://{}'.format(basic_auth_pair))

    kwds = {}
    if opts.local:
        opts.proxy = 'localhost:58080'

    if opts.proxy:
        if opts.driver == 'phantomjs':
            addr = opts.proxy if opts.proxy.startswith('http') else 'http://{}'.format(opts.proxy)
            kwds['service_args'] = ['--proxy', addr]
        else:
            proxy = selenium.webdriver.common.proxy.Proxy()
            proxy.http_proxy = proxy.ftp_proxy = proxy.ssl_proxy = proxy.socks_proxy = opts.proxy
            kwds['proxy'] = proxy

    driver_klass = get_driver(opts.driver)
    browser = driver_klass(**kwds)
    status = None

    event_runner = Runner(browser, status)
    event_runner += [
        BackendLogin(),
        Events(),
        EventsNew(opts.event),
        StockTypeCreator(),
        ReturnEventPageFromTicketPage(),
        TicketCreator(),
        SalesSegmentGroupCreator(),
        JumpSalesSegmentGroupShowPage(),
        SalesSegmentGroupEdit(),
        PDMPCreator(),
        ]
    browser, status = event_runner.run(url, turn=1)

    performance_runner = Runner(browser, status)
    performance_runner += [
        BackendLogin(),
        PerformanceCreator(name=opts.performance),
        PerformanceDetailPage(),
        SeatAllocatorr(),
        ProductCreator(),
        PerformancePublicChanger(),
        ]
    performance_runner.run()

if __name__ == '__main__':
    main()
