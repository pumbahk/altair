# -*- coding:utf-8 -*-
import unittest
import sys
import os
from datetime import datetime

try:
   from functional_tests import AppFunctionalTests, logout, login, get_registry
   from functional_tests import delete_models, find_form
except ImportError:
   sys.path.append(os.path.join(os.path.dirname(__name__), "../../"))
   from functional_tests import AppFunctionalTests, logout, login, get_registry
   from functional_tests import delete_models, find_form

## here. test_promotion
class PromotionFunctionalTests(AppFunctionalTests):
   def tearDown(self):
        from altaircms.asset.models import ImageAsset
        from altaircms.topic.models import PromotionTag
        from altaircms.topic.models import Promotion
        from altaircms.page.models import Page
        from altaircms.plugins.widget.promotion.models import PromotionWidget
        delete_models([Promotion, PromotionTag, Page, ImageAsset, PromotionWidget])


   def _get_promotion(self):
      from altaircms.topic.models import Promotion
      return Promotion.query.first()

   def _count_of_promotion(self):
      from altaircms.topic.models import Promotion
      return Promotion.query.count()

   def _get_image_asset_by_title(self, title):
      from altaircms.asset.models import ImageAsset
      return ImageAsset.query.filter_by(title=title).first()

   def test_goto_login_page_if_not_login(self):
      app = self._getTarget()
      with logout(app):
         app.get("/promotion/list").mustcontain(u"ログインしていません")

   def test_promotion_page_list(self):
      app = self._getTarget()
      with login(app):
         list_response = app.get("/promotion/list")
         list_response.mustcontain(u"一覧")

   def _count_of_promotion_tag(self):
      from altaircms.topic.models import PromotionTag
      return PromotionTag.query.count()

   def _count_of_promotion_page(self):
      from altaircms.plugins.widget.promotion.models import PromotionWidget
      from altaircms.page.models import Page
      return PromotionWidget.query.filter(Page.id==PromotionWidget.page_id).with_entities(Page, PromotionWidget).count()
      
   def test_promotion_tag_create(self):
      app = self._getTarget()
      with login(app):
         from altaircms.auth.models import Organization
         organization = Organization.query.first() # login時にorganizationは作成される
         self.assertEqual(self._count_of_promotion_tag(), 0)

         list_response = app.get("/promotion/list")
         form = find_form(list_response.forms,  action_part="add")
         form.set("tags", "this-is-promotion-tag")
         form.set("organization_id", unicode(organization.id))
         form.submit().mustcontain("this-is-promotion-tag")

         self.assertEqual(self._count_of_promotion_tag(), 1)

   def test_detail_page(self): #toooooooooooooooooooooooo long
      from altaircms.auth.models import Organization
      from altaircms.models import DBSession
      from altaircms.page.models import Page, PageType
      from altaircms.topic.models import PromotionTag
      from altaircms.asset.models import ImageAsset
      from altaircms.plugins.widget.promotion.models import PromotionWidget

      app = self._getTarget()
      with login(app):
         ## tagの作成
         organization = Organization.query.first() # login時にorganizationは作成される
         self.assertEqual(self._count_of_promotion_tag(), 0)

         list_response = app.get("/promotion/list")
         form = find_form(list_response.forms,  action_part="add")
         form.set("tags", u"this-is-promotion-tag, tag, tag0")
         form.set("organization_id", unicode(organization.id))
         form.submit().mustcontain("this-is-promotion-tag")

         created_tag = PromotionTag.query.filter_by(label=u"this-is-promotion-tag").first()
         self.assertEqual(created_tag.label, u"this-is-promotion-tag")


      # page作成 そのpageはpromotion widgetを持つ
      pagetype = PageType.query.filter_by(organization_id=organization.id).first()
      page = Page(name=u"this-is-created-page", organization_id=organization.id, pagetype_id=pagetype.id)
      widget = PromotionWidget(page=page, tag=created_tag)
      DBSession.add(page)

      ## promotionと紐づいたページができる。
      self.assertEqual(self._count_of_promotion_page(), 1)

      ## 画像assetが必要なので作成
      with login(app):
         asset_title = u"this-is-created-image-asset"
         
         form = find_form(app.get("/asset/image").forms, action_part="create")
         form.set("filepath",  ("imageasset-create-image.PNG", ))
         form.set("thumbnail_path", ("imageasset-thumbnail-image.png", ))
         form.set("title", asset_title)
         form.set("tags", u"tag0, tag1, tag2")
         form.set("private_tags", u"ptag")

         form.submit()

         ## 画像が存在
         created_asset = ImageAsset.query.first()
         self.assertTrue(created_asset)

      ## 詳細画面に移動できる
      import transaction
      transaction.commit()
      page = DBSession.merge(page)
      widget = DBSession.merge(widget)
      
      with login(app):
         ## promotion widgetの結びついたページの詳細ページが見れる
         detail_response = app.get("/promotion/page/%s/detail" % page.id)
         detail_response.mustcontain(widget.tag.label)

         ### create
         ## promotionの追加ができる
         create_input_response = detail_response.click(linkid="create_link")
         form = find_form(create_input_response.forms, action_part="create")
         form.set("main_image", 1)
         form.set("tag_content", PromotionTag.query.first().label)
         form.set("text", u"this-is-text-message")
         form.set("link", u"http://www.example.com")
         form.set("publish_open_on", datetime(1900, 1, 1))
         form.set("publish_close_on", datetime(2200, 1, 1))
         
         confirm_response = form.submit()
         form = find_form(confirm_response.forms, action_part="create")

         ## promotionが作成される
         create_redirect_response = form.submit().follow()
         self.assertEqual(self._count_of_promotion(), 1)
         promotion = self._get_promotion()
         self.assertEqual(promotion.text, u"this-is-text-message")
         self.assertEqual(promotion.link, u"http://www.example.com")

         ### update
         ## promotionの更新ができる。
         update_input_response = create_redirect_response.click(index=1, href="/promotion_unit/update/%s/input" % promotion.id)
         form = find_form(update_input_response.forms, action_part="update")
         form.set("text", u"this-is-text-message.updated.updated.updated")
         form.set("display_order", "30")

         confirm_response = form.submit()
         form = find_form(confirm_response.forms, action_part="update")

         ## promotionが更新される
         update_redirect_response = form.submit().follow()
         self.assertEqual(promotion.text, u"this-is-text-message.updated.updated.updated")
         self.assertEqual(promotion.display_order, 30)



         ### delete
         ## promotionが削除できる
         delete_confirm_response = update_redirect_response.click(href="/promotion_unit/delete/%s/confirm" % promotion.id)
         form = find_form(delete_confirm_response.forms, action_part="delete")
         form.submit()

         ## promotionが削除される
         self.assertEqual(self._count_of_promotion(), 0)

if __name__ == "__main__":
   def setUpModule():
      from functional_tests import get_app
      get_app()
   unittest.main()
