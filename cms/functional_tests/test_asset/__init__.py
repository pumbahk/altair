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

import webtest

## here. asset
class AssetFunctionalImageTests(AppFunctionalTests):
    def test_goto_login_page_if_not_login(self):
        app = self._getTarget()
        with logout(app):
            app.get("/asset/").mustcontain(u"ログインしていません")

    def tearDown(self):
        from altaircms.asset.models import ImageAsset, ImageAssetTag
        delete_models([ImageAsset, ImageAssetTag])


    def _count_of_image_asset(self):
        from altaircms.asset.models import ImageAsset
        return ImageAsset.query.count()

    def _get_image_asset_by_title(self, title):
        from altaircms.asset.models import ImageAsset
        return ImageAsset.query.filter_by(title=title).first()

    def _get_static_asset_path(self, path):
        return "/staticasset/"+path

    def test_create_image_asset(self):
        app = self._getTarget()
        self.assertEqual(self._count_of_image_asset(), 0)

        with login(app):
            asset_title = u"this-is-created-image-asset"

            form = find_form(app.get("/asset/image").forms, action_part="create")
            form.set("filepath",  ("imageasset-create-image.PNG", ))
            form.set("thumbnail_path", ("imageasset-thumbnail-image.png", ))
            form.set("title", asset_title)
            form.set("tags", "tag0, tag1, tag2")
            form.set("private_tags", "ptag")

            form.submit()

            ## assetが存在
            self.assertEqual(self._count_of_image_asset(), 1)
            created_asset = self._get_image_asset_by_title(asset_title)

            ## 画像が存在
            mainimage = app.get(self._get_static_asset_path(created_asset.filepath))
            self.assertEqual(mainimage.status_int, 200)
            thumbnail_image = app.get(self._get_static_asset_path(created_asset.thumbnail_path))
            self.assertEqual(thumbnail_image.status_int, 200)

    def test_create_image_asset_thumnaill_is_auto_create(self):
        app = self._getTarget()
        self.assertEqual(self._count_of_image_asset(), 0)

        with login(app):
            asset_title = u"this-is-created-image-asset--without-thumbnail"

            form = find_form(app.get("/asset/image").forms, action_part="create")
            form.set("filepath",  ("imageasset-update-image.png", ))
            form.set("thumbnail_path", "")
            form.set("title", asset_title)
            form.submit()

            ## assetが存在
            self.assertEqual(self._count_of_image_asset(), 1)
            created_asset = self._get_image_asset_by_title(asset_title)

            ## 画像が存在
            mainimage = app.get(self._get_static_asset_path(created_asset.filepath))
            self.assertEqual(mainimage.status_int, 200)
            thumbnail_image = app.get(self._get_static_asset_path(created_asset.thumbnail_path))
            self.assertEqual(thumbnail_image.status_int, 200)

    def test_delete_image_asset(self):
        app = self._getTarget()
        self.assertEqual(self._count_of_image_asset(), 0)

        with login(app):
            asset_title = u"this-is-created-image-asset"

            form = find_form(app.get("/asset/image").forms, action_part="create")
            form.set("filepath",  ("imageasset-create-image.PNG", ))
            form.set("thumbnail_path", ("imageasset-thumbnail-image.png", ))
            form.set("title", asset_title)
            form.set("tags", "tag0, tag1, tag2")
            form.set("private_tags", "ptag")

            form.submit()

            ## assetが存在
            self.assertEqual(self._count_of_image_asset(), 1)
            created_asset = self._get_image_asset_by_title(asset_title)

            ### delete
            form = find_form(app.get("/asset/image/%s/delete" % created_asset.id).forms, action_part="delete").submit()
            
            ## assetがなくなる
            self.assertEqual(self._count_of_image_asset(), 0)

            ## 画像が消える
            with self.assertRaises(webtest.AppError):
                app.get(self._get_static_asset_path(created_asset.filepath))
                app.get(self._get_static_asset_path(created_asset.thumbnail_path))


    def test_update_image_asset(self):
        app = self._getTarget()
        self.assertEqual(self._count_of_image_asset(), 0)

        with login(app):
            ## create
            asset_title = u"this-is-created-image-asset"

            form = find_form(app.get("/asset/image").forms, action_part="create")
            form.set("filepath",  ("imageasset-create-image.PNG", ))
            form.set("thumbnail_path", ("imageasset-thumbnail-image.png", ))
            form.set("title", asset_title)
            form.set("tags", "tag0, tag1, tag2")
            form.set("private_tags", "ptag")

            form.submit()

            created_asset = self._get_image_asset_by_title(asset_title)
            created_asset_size = created_asset.size
            created_asset_filepath = created_asset.filepath
            self.assertEquals(created_asset.version_counter, 0)

            ### update title
            asset_title = u"update-asset"

            form = find_form(app.get("/asset/image/%s/input" % created_asset.id).forms, action_part="update")
            form.set("filepath",  "")
            form.set("thumbnail_path", "")
            form.set("title", asset_title)
            form.set("tags", "tag-is-updated")
            form.set("private_tags", "ptag, ptag2")

            form.submit()

            ## タイトルは変わる
            self.assertEqual(self._count_of_image_asset(), 1)
            updated_asset = self._get_image_asset_by_title(asset_title)
            self.assertEqual(updated_asset.title, asset_title)
            self.assertEquals(updated_asset.version_counter, 1)

            ## 画像は変わらない
            self.assertEqual(updated_asset.size,  created_asset.size)            
            self.assertEqual(updated_asset.filepath, created_asset_filepath)

            ### update image
            created_asset = self._get_image_asset_by_title(asset_title)
            asset_title = u"update-asset"

            form = find_form(app.get("/asset/image/%s/input" % created_asset.id).forms, action_part="update")
            form.set("filepath",  ("imageasset-update-image.png", ))
            form.set("thumbnail_path", "")
            form.set("title", asset_title)
            form.set("tags", "tag-is-updated")
            form.set("private_tags", "ptag, ptag2")

            form.submit()

            self.assertEqual(self._count_of_image_asset(), 1)
            updated_asset2 = self._get_image_asset_by_title(asset_title)
            
            ## 画像を変更しても保存先も変わる
            self.assertEqual(updated_asset2.filepath, updated_asset.filename_with_version(created_asset_filepath, 2))
            ## ただし保存されているファイルは変わる
            self.assertNotEqual(updated_asset2.size, created_asset_size)
            

class AssetFunctionalMovieTests(AppFunctionalTests):
    ## movie asset
    def tearDown(self):
        from altaircms.asset.models import MovieAsset, MovieAssetTag
        delete_models([MovieAsset, MovieAssetTag])

    def _get_static_asset_path(self, path):
        return "/staticasset/"+path

    def _count_of_movie_asset(self):
        from altaircms.asset.models import MovieAsset
        return MovieAsset.query.count()

    def _get_movie_asset_by_title(self, title):
        from altaircms.asset.models import MovieAsset
        return MovieAsset.query.filter_by(title=title).first()

    def test_create_movie_asset(self):
        app = self._getTarget()
        self.assertEqual(self._count_of_movie_asset(), 0)

        with login(app):
            asset_title = u"this-is-created-movie-asset"

            form = find_form(app.get("/asset/movie").forms, action_part="create")
            form.set("filepath",  ("movieasset-create-movie.mp4", ))
            form.set("placeholder", ("imageasset-thumbnail-image.png", ))
            form.set("title", asset_title)
            form.set("tags", "tag0, tag1, tag2")
            form.set("private_tags", "ptag")

            form.submit()

            ## assetが存在
            self.assertEqual(self._count_of_movie_asset(), 1)
            created_asset = self._get_movie_asset_by_title(asset_title)
            self.assertEqual(created_asset.title, asset_title)
            # self.assertTrue(created_asset.width)
            # self.assertTrue(created_asset.height)

            ## movieとthumbnail(placeholder)が存在
            mainmovie = app.get(self._get_static_asset_path(created_asset.filepath))
            self.assertEqual(mainmovie.status_int, 200)

            thumbnail_movie = app.get(self._get_static_asset_path(created_asset.thumbnail_path))
            self.assertEqual(thumbnail_movie.status_int, 200)

    def test_update_movie_asset(self):
        app = self._getTarget()
        self.assertEqual(self._count_of_movie_asset(), 0)

        with login(app):
            ## create
            asset_title = u"this-is-created-movie-asset"

            form = find_form(app.get("/asset/movie").forms, action_part="create")
            form.set("filepath",  ("movieasset-create-movie.mp4", ))
            form.set("placeholder", ("imageasset-thumbnail-image.png", ))
            form.set("title", asset_title)
            form.set("tags", "tag0, tag1, tag2")
            form.set("private_tags", "ptag")

            form.submit()

            created_asset = self._get_movie_asset_by_title(asset_title)
            created_asset_filepath = created_asset.filepath
            created_placeholder_path = created_asset.thumbnail_path
            created_placeholder_response = app.get(self._get_static_asset_path(created_placeholder_path)).body

            ### update title
            asset_title = u"update-asset"

            form = find_form(app.get("/asset/movie/%s/input" % created_asset.id).forms, action_part="update")
            form.set("filepath",  "")
            form.set("placeholder", "")
            form.set("title", asset_title)
            form.set("tags", "tag-is-updated")
            form.set("private_tags", "ptag, ptag2")

            form.submit()

            ## タイトルは変わる
            self.assertEqual(self._count_of_movie_asset(), 1)
            updated_asset = self._get_movie_asset_by_title(asset_title)
            self.assertEqual(updated_asset.title, asset_title)

            ## 動画は変わらない
            self.assertEqual(updated_asset.filepath, created_asset_filepath)
            self.assertEqual(updated_asset.thumbnail_path, created_placeholder_path)
            self.assertEqual(app.get(self._get_static_asset_path(updated_asset.thumbnail_path)).body[:100], 
                                created_placeholder_response[:100])


            ### update movie
            created_asset = self._get_movie_asset_by_title(asset_title)
            asset_title = u"update-asset"

            form = find_form(app.get("/asset/movie/%s/input" % created_asset.id).forms, action_part="update")
            form.set("filepath",  "")
            form.set("placeholder", ("imageasset-update-image.png", ))
            form.set("title", asset_title)
            form.set("tags", "tag-is-updated")
            form.set("private_tags", "ptag, ptag2")

            form.submit()

            self.assertEqual(self._count_of_movie_asset(), 1)
            updated_asset2 = self._get_movie_asset_by_title(asset_title)
            
            ## placeholderを変更しても保存先は変わらない
            self.assertEqual(updated_asset2.filepath, created_asset_filepath)
            self.assertEqual(updated_asset2.thumbnail_path, updated_asset2.filename_with_version(created_placeholder_path, 2))

            ## ただし保存されているファイルは変わる
            self.assertNotEqual(app.get(self._get_static_asset_path(updated_asset2.thumbnail_path)).body[:100], 
                                created_placeholder_response[:100])

    def test_delete_movie_asset(self):
        app = self._getTarget()
        self.assertEqual(self._count_of_movie_asset(), 0)

        with login(app):
            ## create
            asset_title = u"this-is-created-movie-asset"

            form = find_form(app.get("/asset/movie").forms, action_part="create")
            form.set("filepath",  ("movieasset-create-movie.mp4", ))
            form.set("placeholder", ("imageasset-thumbnail-image.png", ))
            form.set("title", asset_title)
            form.set("tags", "tag0, tag1, tag2")
            form.set("private_tags", "ptag")

            form.submit()

            ## assetが存在
            self.assertEqual(self._count_of_movie_asset(), 1)
            created_asset = self._get_movie_asset_by_title(asset_title)

            ### delete
            form = find_form(app.get("/asset/movie/%s/delete" % created_asset.id).forms, action_part="delete").submit()
            
            ## assetがなくなる
            self.assertEqual(self._count_of_movie_asset(), 0)

            ## 画像が消える
            with self.assertRaises(webtest.AppError):
                app.get(self._get_static_asset_path(created_asset.filepath))
                app.get(self._get_static_asset_path(created_asset.thumbnail_path))


class AssetFunctionalFlashTests(AppFunctionalTests):
    def tearDown(self):
        from altaircms.asset.models import FlashAsset, FlashAssetTag
        delete_models([FlashAsset, FlashAssetTag])

    def _get_static_asset_path(self, path):
        return "/staticasset/"+path

    ## flash asset
    def _count_of_flash_asset(self):
        from altaircms.asset.models import FlashAsset
        return FlashAsset.query.count()

    def _get_flash_asset_by_title(self, title):
        from altaircms.asset.models import FlashAsset
        return FlashAsset.query.filter_by(title=title).first()

    def test_create_flash_asset(self):
        app = self._getTarget()
        self.assertEqual(self._count_of_flash_asset(), 0)

        with login(app):
            asset_title = u"this-is-created-flash-asset"

            form = find_form(app.get("/asset/flash").forms, action_part="create")
            form.set("filepath",  ("flashasset-create-flash.swf", ))
            form.set("placeholder", ("imageasset-thumbnail-image.png", ))
            form.set("title", asset_title)
            form.set("tags", "tag0, tag1, tag2")
            form.set("private_tags", "ptag")

            form.submit()

            ## assetが存在
            self.assertEqual(self._count_of_flash_asset(), 1)
            created_asset = self._get_flash_asset_by_title(asset_title)
            self.assertEqual(created_asset.title, asset_title)
            self.assertTrue(created_asset.width)
            self.assertTrue(created_asset.height)

            ## flashとthumbnail(placeholder)が存在
            mainflash = app.get(self._get_static_asset_path(created_asset.filepath))
            self.assertEqual(mainflash.status_int, 200)

            thumbnail_flash = app.get(self._get_static_asset_path(created_asset.thumbnail_path))
            self.assertEqual(thumbnail_flash.status_int, 200)

    def test_update_flash_asset(self):
        app = self._getTarget()
        self.assertEqual(self._count_of_flash_asset(), 0)

        with login(app):
            ## create
            asset_title = u"this-is-created-flash-asset"

            form = find_form(app.get("/asset/flash").forms, action_part="create")
            form.set("filepath",  ("flashasset-create-flash.swf", ))
            form.set("placeholder", ("imageasset-thumbnail-image.png", ))
            form.set("title", asset_title)
            form.set("tags", "tag0, tag1, tag2")
            form.set("private_tags", "ptag")

            form.submit()

            created_asset = self._get_flash_asset_by_title(asset_title)
            created_asset_filepath = created_asset.filepath
            created_placeholder_path = created_asset.thumbnail_path
            created_flash_response = app.get(self._get_static_asset_path(created_asset_filepath)).body
            created_placeholder_response = app.get(self._get_static_asset_path(created_placeholder_path)).body

            ### update title
            asset_title = u"update-asset"

            form = find_form(app.get("/asset/flash/%s/input" % created_asset.id).forms, action_part="update")
            form.set("filepath",  "")
            form.set("placeholder", "")
            form.set("title", asset_title)
            form.set("tags", "tag-is-updated")
            form.set("private_tags", "ptag, ptag2")
            
            form.submit()

            ## タイトルは変わる
            self.assertEqual(self._count_of_flash_asset(), 1)
            updated_asset = self._get_flash_asset_by_title(asset_title)
            self.assertEqual(updated_asset.title, asset_title)

            ## flashは変わらない
            self.assertEqual(updated_asset.filepath, created_asset_filepath)
            self.assertEqual(updated_asset.thumbnail_path, created_placeholder_path)
            self.assertEqual(app.get(self._get_static_asset_path(updated_asset.filepath)).body[:100], 
                             created_flash_response[:100])
            self.assertEqual(app.get(self._get_static_asset_path(updated_asset.thumbnail_path)).body[:100], 
                             created_placeholder_response[:100])


            ### update flash
            created_asset = self._get_flash_asset_by_title(asset_title)
            asset_title = u"update-asset"

            form = find_form(app.get("/asset/flash/%s/input" % created_asset.id).forms, action_part="update")
            form.set("filepath",  ("flashasset-update-flash.swf", ))
            form.set("placeholder", ("imageasset-update-image.png", ))
            form.set("title", asset_title)
            form.set("tags", "tag-is-updated")
            form.set("private_tags", "ptag, ptag2")

            form.submit()

            self.assertEqual(self._count_of_flash_asset(), 1)
            updated_asset2 = self._get_flash_asset_by_title(asset_title)
            
            ## placeholderを変更しても保存先は変わらない
            self.assertEqual(updated_asset2.filepath, updated_asset2.filename_with_version(created_asset_filepath, 2))
            self.assertEqual(updated_asset2.thumbnail_path, updated_asset2.filename_with_version(created_placeholder_path))

            ## ただし保存されているファイルは変わる
            self.assertNotEqual(app.get(self._get_static_asset_path(updated_asset.thumbnail_path)).body[:100], 
                             created_flash_response[:100])
            self.assertNotEqual(app.get(self._get_static_asset_path(updated_asset2.thumbnail_path)).body[:100], 
                                created_placeholder_response[:100])



    def test_delete_flash_asset(self):
        app = self._getTarget()
        self.assertEqual(self._count_of_flash_asset(), 0)

        with login(app):
            ## create
            asset_title = u"this-is-created-flash-asset"

            form = find_form(app.get("/asset/flash").forms, action_part="create")
            form.set("filepath",  ("flashasset-create-flash.swf", ))
            form.set("placeholder", ("imageasset-thumbnail-image.png", ))
            form.set("title", asset_title)
            form.set("tags", "tag0, tag1, tag2")
            form.set("private_tags", "ptag")

            form.submit()

            ## assetが存在
            self.assertEqual(self._count_of_flash_asset(), 1)
            created_asset = self._get_flash_asset_by_title(asset_title)

            ### delete
            form = find_form(app.get("/asset/flash/%s/delete" % created_asset.id).forms, action_part="delete").submit()
            
            ## assetがなくなる
            self.assertEqual(self._count_of_flash_asset(), 0)

            ## flashが消える
            with self.assertRaises(webtest.AppError):
                app.get(self._get_static_asset_path(created_asset.filepath))
                app.get(self._get_static_asset_path(created_asset.thumbnail_path))

if __name__ == "__main__":
   unittest.main()
