.. -*- coding: utf-8 -*-

**************************************************
altair用Lock機構
**************************************************

INSTALL
================

pipでinstallするには次のようにします。
::

    $ cd /PATH/TO/YOUR/ALTAIR/ROOT
    $ pip install ./altairlib/altair.multilock

HOW TO USE IT
================

このモジュールは多重起動を防止するためのライブラリとして作成されました。
MultiStartLock() はその要求に答えます。

::

    >>> try:
    >>>     timeout = 10 # sec
    >>>     name = 'LOCK_NAME' # lock name
    >>>     with MultiStartLock(name=name, timeout=timeout):
    >>>         pass # statements
    >>> except AlreadyStartUpError as err:
    >>>     pass # statements


with 構文内にある時はロックを取得した状態です。
ロックが取得できない場合は AlreadyStartUpErrorが送出されます。

name引数は取得するロックの名称です。必ず指定する必要があります。
timeout引数はロック取得のための待ち時間です。単位は秒です。デフォルトは10です。
