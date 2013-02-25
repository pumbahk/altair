# -*- coding:utf-8 -*-
import unittest
from datetime import datetime
import sys
import os

try:
    from functional_tests.utils import get_here, create_api_key, get_pushed_data_from_backend
    from functional_tests import AppFunctionalTests, logout, login, get_registry
    from functional_tests import delete_models, find_form
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__name__), "../../"))
    from functional_tests.utils import get_here, create_api_key, get_pushed_data_from_backend
    from functional_tests import AppFunctionalTests, logout, login, get_registry, get_here
    from functional_tests import delete_models, find_form

## here. test_eventpage
CORRECT_API_HEADER_NAME = 'X-Altair-Authorization'

class PageTests(AppFunctionalTests):
    @classmethod
    def setUpClass(cls):
        """layoutの登録にpagetypeが必要なのです """
        from altaircms.models import DBSession
        from altaircms.page.models import PageType
        from altaircms.auth.models import Organization

        app = cls._getTarget()
        with login(app):
            organization = Organization.query.first() # login時にorganization, pagetypeは作成される
            pagetype = PageType.query.filter_by(organization_id=organization.id).first()
            DBSession.flush()

            ## layoutも作ります
            create_page = app.get("/layout/pagetype/%d/create/input" % pagetype.id)
            layout_title = u"this-is-created-layout-template"
            form = find_form(create_page.forms, action_part="create")
            form.set("title", layout_title)
            form.set("template_filename", "saved-template-name") ## htmlがない
            form.set("filepath", ("layout-create-template.html", ))
            form.submit()

    @classmethod
    def tearDownClass(cls):
        from altaircms.auth.models import APIKey
        from altaircms.page.models import PageSet, Page
        from altaircms.models import Performance, SalesSegment, Ticket
        delete_models([Performance, SalesSegment, Ticket, APIKey, PageSet, Page])

    def test_goto_login_page_if_not_login(self):
       app = self._getTarget()
       from altaircms.page.models import PageType
       pagetype = PageType.query.first()
       with logout(app):
          app.get("/page/pagetype/%s/list" % pagetype.name).mustcontain(u"ログインしていません")

    def test_it(self):
        from altaircms.page.models import PageType
        app = self._getTarget()
        from altaircms.auth.models import Organization
        with login(app):
            organization = Organization.query.first() # login時にorganization, pagetypeは作成される
            pagetype = PageType.query.filter_by(organization_id=organization.id).first()
            list_page_response = app.get("/page/pagetype/%s/list" % pagetype.name)
            pageset_create_input_response = list_page_response.click(href="/page/create/input")

            form = find_form(pageset_create_input_response.forms, action_part="create")
            form.set("name", u"demo-page")
            form.set("url", u"demo-url")
            form.set("title", u"this-is-page-title")
            form.set("publish_begin", datetime(1900, 1, 1))
            form.set("description", u"ababababbaba-ababababbaba-ababababbaba-ababababbaba-ababababbaba")
            form.set("tags", u"event demo page tag public")
            form.set("private_tags", u"event demo page tag public")
            confirm_response = form.submit()

            form = find_form(confirm_response.forms, action_part="create")
            submit_response = form.submit()
            
            self.assertEqual(submit_response.status_int, 302)

            # page is created!!,  to be continued ...

        
if __name__ == "__main__":
    def setUpModule():
        from functional_tests import get_app
        get_app()
    unittest.main()
