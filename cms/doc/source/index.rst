.. ticketstar cms documentation master file, created by
   sphinx-quickstart on Fri Jan  6 16:08:12 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

==========================================
Ticketstar CMS Document (|today|)
==========================================

動作環境
=============

.. toctree::
   :maxdepth: 2

   requirement
   browser


画面イメージ
=============

利用する画面レイアウトを定義する。

.. toctree::
   :maxdepth: 2

   layout/front
   layout/cms


ユースケース
============

.. toctree::
   :maxdepth: 2

   cms


仕様
============

.. toctree::

   spec/target_structure
   spec/backend_communicate
   spec/storage
   spec/model

   objects/list


CMS機能
==========

.. toctree::
   :maxdepth: 2

   widgets/index
   widgets/list

   about_data_management


CMS以外の機能
=========================

.. toctree::
   :maxdepth: 2

   functions/index



調査
=========

.. toctree::

   research/kotti.rst
   research/fantastic.rst


スケジュール
======================

.. toctree::

   schedule.rst


付録
=====

.. toctree::

    appendix/rakute_purchase_api_code_list

用語
=========

.. glossary::

 販売者
   バックエンド側のCMSを操作。売るチケットなどを作成する人

 CMS管理者
   CMSの管理を行うオペレータ。チケットスター社内の人の想定

 サイト管理者
   フロントエンドCMSを利用して、商品ページ用のデータを登録する人のこと

 サイト利用者
   サイトに訪れてチケットを購入する人

 商品ページ
   売るチケットの紹介や購入などを行うウェブサイト

 フロントエンドCMS
   商品ページ用のデータ登録を行うCMS

 バックエンド
   票券監理など裏側の重要なデータを管理するシステム

 券種
   チケットの種類のこと。「S席大人」など。

 配席
   席＝在庫のこと。

 配券
   席の販売枠の割り当て。


TODO
====

.. todolist::


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
