CMSの管理対象について
========================================

CMSを利用した作業体制のイメージ
--------------------------------------------------------------------------------

.. note:: ASP販売を今後検討している(それは2011/7/1以降。ただしそれを考慮に入れて開発する必要はある。)

simple
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

*クライアントの数1、管理するサイトの数1(初回の状態)*

.. blockdiag::

   diagram {
   group {
      label = "チケットスター";
      A [label=販売員A];
      B [label=販売員B];
      C [label=販売員C];
      D [label=販売員D];
   } 

   root [label="販売者(クライアント)"];
   site [label="販売サイト(楽天チケット)"];
   root -> A [label="a", textcolor="red"];
   A -> site [label="a*",textcolor="green"];
   root -> B -> site;
   root -> C -> site;
   root -> D -> site;
   }

クライアントから配布されるイベントa用のチケットを、チケットスターの販売員が、販売サイトで売ろうとする。
この時、チケットa*用のページとしてイベント詳細ページを作成する。

complex
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. note:: クライアントの数 = サイト数?

*２つのクライアントから同じイベントのチケットを別々に配布され別々のサイトで売る場合*

.. blockdiag::

   diagram {
   group {
      label = "チケットスター";
      A [label=販売員A];
      B [label=販売員B];
      C [label=販売員C];
      D [label=販売員D];
   } 

   root1 [label="販売者X(クライアントX)"];
   site1 [label="販売サイト(楽天チケット)"];
   root1 -> A [label="a", textcolor="red"];
   A -> site1 [label="a*",textcolor="green"];
   root1 -> B -> site1;
   root1 -> C -> site1;
   root1 -> D -> site1;

   root2 [label="販売者Y(クライアント)Y"];
   site2 [label="販売サイト(別のサイト)"];
   root2 -> A [label="a", textcolor="red"];
   A -> site2 [label="a**",textcolor="green"];
   root2 -> B -> site2;
   root2 -> C -> site2;
   root2 -> D -> site2;
   }

２つのクライアントから同じイベントaのチケットを別々に配布された場合は、各販売サイト毎に別々のページを登録することができる必要がある。

+ 楽天チケットのサイトではイベントa用のページa*を作成
+ 別の販売サイトではイベントa用のページa**を作成

*複数のASP利用会社にチケットが配布された場合(ASP販売開始後)*

.. blockdiag::

   diagram {
   group {
      label = "チケットスター";
      color = "lightgreen";
      A [label=販売員A];
      B [label=販売員B];
      C [label=販売員C];
      D [label=販売員D];
   } 

   root1 [label="販売者X(クライアントX)"];
   site1 [label="販売サイト(楽天チケット)"];
   root1 -> A [label="a,b", textcolor="red"];
   A -> site1 [label="a*,b*",textcolor="green"];
   root1 -> B -> site1;
   root1 -> C -> site1;
   root1 -> D -> site1;

   group {
      label = "ASP利用社Foo";
      F [label=販売員F];
      G [label=販売員G];
   } 

   site2 [label="販売サイト(別のサイト)"];
   root1 -> G [label="a", textcolor="red"];
   G -> site2 [label="a**",textcolor="green"];
   root1 -> F -> site2;
   }

クライアントから配布されるチケットをチケットスターの販売員が販売サイトで売る。

+ チケットスターの販売員はイベントaのチケットを、楽天チケットでa*として売る
+ チケットスターの販売員はイベントbのチケットを、楽天チケットでb*として売る
+ ASP利用社Fooの販売員はイベントaのチケットを、別のサイトでa**として売る

ただし、

+ (チケットスターの販売員は、a**のページの情報を見ることができない)
+ (ASP利用者Fooの販売員は、a*のページの情報を見ることができない)
+ (ASP利用者Fooの販売員はイベントbの情報を見ることができない)

1つのCMSが管理する対象
----------------------------------------

チケット販売員のフロントエンドCMS上での可視範囲は上記の通りだが、全ての情報をひとつのCMSシステムで管理する。

.. blockdiag::

   diagram {
	 group {
       color = "#aaaaff";
	   label = "CMS管理";
	   A [label = "チケットスター", color="lightgreen"];
	   B [label = "ASP利用社Foo", color="orange"];
	 }
     root [label="販売者X(クライアントX)"];
     site1 [label="販売サイト(楽天チケット)"];
     site2 [label="販売サイト(別のサイト)"];
	 root -> A [label="a",textcolor="red"];
     A -> site1[label="a*",textcolor="green"];
	 root -> B [label="a",textcolor="red"];
     B -> site2[label="a**",textcolor="green"];
   }

CMSでそれぞれのデータを管理する際の個数の関係は以下の通り。

:DB: 1
:ASP利用者の数: 1 -> N(ASP販売後)
:管理するサイトの数: 1 -> M(?)

となる。
ASP販売後のことも考慮に入れてDBの設計をする必要がある。

ページ生成時時のパーミッション
----------------------------------------

+ ページ単位で、編集可能なパーミッションを設ける
