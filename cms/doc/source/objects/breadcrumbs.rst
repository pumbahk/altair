.. _object-breadcrumbs:

パンくずオブジェクト
---------------------------

フロント側の表示で使用する想定。

.. code-block:: python

 {
     'breadcrumbs': [ # 階層分、必要なだけlistを持つ
         {'url': str, 'label': unicode},
         {'url': str, 'label': unicode},
         {'url': str, 'label': unicode} # urlが無ければリンクなし、強調表示
     ]
 }


see also: :ref:`widget-breadcrumbs`

.. todo::

   ページそのものに階層を保持する必要があるのではないか
   http://dev.ticketstar.jp/redmine-altair/issues/154
