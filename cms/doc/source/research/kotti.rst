========================================
フロントエンドCMSについて(Kotti)
========================================

Kottiが使えるかもしれない。

概要
----------------------------------------

KottiはpyramidベースのシンプルなCMS。

機能
----------------------------------------

+ ユーザ認証・監理(認証処理は付けかえ可能)

   + user,groupを選択できる

+ WYSIWIGエディタ
+ CMS(内容の登録・編集・削除)

demo http://kottidemo.danielnouri.org/

widgetの表示位置に対応するフックが用意されている

:: 

  class RenderLeftSlot(ObjectEvent):
	  name = u'left'

  class RenderRightSlot(ObjectEvent):
	  name = u'right'

  class RenderAboveContent(ObjectEvent):
	  name = u'abovecontent'

  class RenderBelowContent(ObjectEvent):
	  name = u'belowcontent'

  class RenderInHead(ObjectEvent):
	  name = u'inhead'

  class RenderBeforeBodyEnd(ObjectEvent):
	  name = u'beforebodyend'

改修必要そうなところ
----------------------------------------

CMS側

+ widgetの機能

商品サイト側

+ css
+ パンくずがユーザサイトにはついていない(CMS側にのみ付いている)
+ widgetのレンダリング

