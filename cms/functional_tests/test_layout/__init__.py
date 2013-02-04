# -*- coding:utf-8 -*-
import unittest
import sys
import os

try:
   from functional_tests import AppFunctionalTests, logout, login, get_registry, get_here
   from functional_tests import delete_models, find_form
except ImportError:
   sys.path.append(os.path.join(os.path.dirname(__name__), "../../"))
   from functional_tests import AppFunctionalTests, logout, login, get_registry, get_here
   from functional_tests import delete_models, find_form
   
## here. layout


class LayoutFunctionalTests(AppFunctionalTests):
    def test_goto_login_page_if_not_login(self):
        app = self._getTarget()
        with logout(app):
            app.get("/asset/").mustcontain(u"ログインしていません")

    PAGETYPE_ID = 1
    @classmethod
    def setUpClass(cls):
        """layoutの登録にpagetypeが必要なのです """
        from altaircms.models import DBSession
        from altaircms.page.models import PageType
        from altaircms.auth.models import Organization

        with login(cls._getTarget()):
           organization = Organization.query.first() # login時にorganizationは作成される
           DBSession.add(PageType(id=cls.PAGETYPE_ID,  name=u"portal", organization_id=organization.id))
           import transaction
           transaction.commit()

    @classmethod
    def tearDownClass(cls):
        """layoutの登録にpagetypeが必要なのです """
        from altaircms.page.models import PageType
        delete_models([PageType])

    def tearDown(self):
        from altaircms.layout.models import Layout
        delete_models([Layout])

    def _count_of_layout(self):
        from altaircms.layout.models import Layout
        return Layout.query.count()

    def _get_layout_by_title(self, layout_title):
        from altaircms.layout.models import Layout
        return Layout.query.filter_by(title=layout_title).first()
        
    def test_create_layout(self):
        app = self._getTarget()
        with login(app):
            ## pagetype毎にレイアウト作成ページがあります
            create_page = app.get("/layout/pagetype/%d/create/input" % self.PAGETYPE_ID)
            self.assertEqual(create_page.status_int, 200)

            layout_title = u"this-is-created-layout-template"

            form = find_form(create_page.forms, action_part="create")
            form.set("title", layout_title)
            form.set("template_filename", "saved-template-name.html")
            form.set("filepath", ("layout-create-template.html", ))
            
            form.submit()

            ## layoutが存在
            self.assertEqual(self._count_of_layout(), 1)
            created_layout = self._get_layout_by_title(layout_title)
            self.assertEqual(created_layout.template_filename, "saved-template-name.html")

            ## 登録されたファイルの存在確認
            layout_directory = get_registry().settings["altaircms.layout_directory"]
            from altaircms.auth.models import Organization
            organization = Organization.query.first() # login時にorganizationは作成される

            ## 保存先は指定したディレクトリ/{Organization.short_name}/指定したファイル名
            saved_template_filename = os.path.join(layout_directory, organization.short_name, "saved-template-name.html")
            self.assertTrue(os.path.exists(saved_template_filename))

    def test_crate_layout_without_extname(self): #move to unittest
        app = self._getTarget()
        with login(app):
            create_page = app.get("/layout/pagetype/%d/create/input" % self.PAGETYPE_ID)
            self.assertEqual(create_page.status_int, 200)

            layout_title = u"this-is-created-layout-template"

            form = find_form(create_page.forms, action_part="create")
            form.set("title", layout_title)
            form.set("template_filename", "saved-template-name") ## htmlがない
            form.set("filepath", ("layout-create-template.html", ))
            
            form.submit()

            ## layoutが存在
            self.assertEqual(self._count_of_layout(), 1)
            created_layout = self._get_layout_by_title(layout_title)
            self.assertEqual(created_layout.template_filename, "saved-template-name.html") #htmlが補われる

            ## 登録されたファイルの存在確認
            layout_directory = get_registry().settings["altaircms.layout_directory"]
            from altaircms.auth.models import Organization
            organization = Organization.query.first() # login時にorganizationは作成される

            ## 保存先は指定したディレクトリ/{Organization.short_name}/指定したファイル名
            saved_template_filename = os.path.join(layout_directory, organization.short_name, "saved-template-name.html")
            self.assertTrue(os.path.exists(saved_template_filename))
        
    def test_update_layout(self):
        app = self._getTarget()
        with login(app):
            ## create
            create_page = app.get("/layout/pagetype/%d/create/input" % self.PAGETYPE_ID)
            self.assertEqual(create_page.status_int, 200)

            layout_title = u"this-is-created-layout-template"

            form = find_form(create_page.forms, action_part="create")
            form.set("title", layout_title)
            form.set("template_filename", "saved-template-name.html")
            form.set("filepath", ("layout-create-template.html", ))
            
            form.submit()

            created_layout = self._get_layout_by_title(layout_title)
            created_layout_title = created_layout.title
            created_layout_template_filename = created_layout.template_filename

            ## update file not changed
            update_page = app.get("/layout/%d/pagetype/%d/update/input" % (created_layout.id, self.PAGETYPE_ID))
            self.assertEqual(update_page.status_int,200)
            layout_title = u"this-is-*updated*-layout-template"

            form = find_form(update_page.forms, action_part="update")
            form.set("title", layout_title)
            form.set("template_filename", "this-name-is-changed. but-filepath-is-empty. so-not-updated-this")
            form.set("filepath", "")
            
            form.submit()

            ## 更新されるので数は変わらない
            self.assertEqual(self._count_of_layout(), 1)
            
            ## タイトルは変わっている
            updated_layout = self._get_layout_by_title(u"this-is-*updated*-layout-template")
            self.assertNotEqual(updated_layout.title, created_layout_title)            

            ## 保存ファイル名は変更されない。変更用のファイルが渡されていないので
            self.assertEqual(updated_layout.template_filename, created_layout_template_filename)            



            ## update file changed
            update_page = app.get("/layout/%d/pagetype/%d/update/input" % (created_layout.id, self.PAGETYPE_ID))
            self.assertEqual(update_page.status_int,200)

            form = find_form(update_page.forms, action_part="update")
            form.set("template_filename", "updated")
            form.set("filepath", ("layout-update-template.html", ))
            form.submit()

            ## 更新されるので数は変わらない
            self.assertEqual(self._count_of_layout(), 1)

            ## 保存ファイル名も変更される
            updated_layout = self._get_layout_by_title(u"this-is-*updated*-layout-template")            
            self.assertNotEqual(updated_layout.template_filename, created_layout_template_filename)            

            ## 登録されたファイルの存在確認
            layout_directory = get_registry().settings["altaircms.layout_directory"]
            from altaircms.auth.models import Organization
            organization = Organization.query.first() # login時にorganizationは作成される

            ## 保存先は指定したディレクトリ/{Organization.short_name}/指定したファイル名
            saved_template_filename = os.path.join(layout_directory, organization.short_name, "updated.html")
            self.assertTrue(os.path.exists(saved_template_filename))

    def test_delete_layout(self):
        app = self._getTarget()
        with login(app):
            ## create
            create_page = app.get("/layout/pagetype/%d/create/input" % self.PAGETYPE_ID)
            self.assertEqual(create_page.status_int, 200)

            layout_title = u"this-is-created-layout-template"

            form = find_form(create_page.forms, action_part="create")
            form.set("title", layout_title)
            form.set("template_filename", "saved-template-name.html")
            form.set("filepath", ("layout-create-template.html", ))
            
            form.submit()

            created_layout = self._get_layout_by_title(layout_title)

            ## delete
            confirm_page = app.get("/layout/delete/%d/confirm" % (created_layout.id))
            self.assertEqual(confirm_page.status_int,200)
            
            form = find_form(confirm_page.forms, action_part="delete")
            response = form.submit().follow()
            self.assertEqual(response.status_int, 200)
            self.assertEqual(self._count_of_layout(), 0)

if __name__ == "__main__":
   unittest.main()
