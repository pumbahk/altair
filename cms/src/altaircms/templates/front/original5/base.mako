## base.makoからイベント詳細のために必要なブロックを取り除いたもの
## これにより元のページとは異なりイベント詳細中に料金を指定することができない。
##

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
  <head>
    <title><%block name="title"></%block></title>

<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<meta http-equiv="Content-Style-Type" content="text/css">
<meta http-equiv="Content-Script-Type" content="text/javascript">
<meta name="description" content="<%block name="description"/>">
<meta name="keywords" content="<%block name="keywords"/>">

<%block name="css_prerender">
</%block>

<%block name="js_prerender">
</%block>

<script type="text/javascript">
  $(function(){
  <%block name="js_postrender"/>
  });
</script>

</head>
<body>
  <div class="page page-one_column">  
    <div class="page-header">
      <div class="page-header-content">
        <%block name="page_header_content"/>
      </div>
      <div class="notice">
        <%block name="notice"/>
      </div>
    </div>
    <div class="page-main">
      <div class="page-main-header">
        <%block name="page_main_header"/>
      </div>
      <div class="page-main-main">
        <div class="page-main-main-content">
          <%block name="page_main_title"/>
          <div class="description_and_image">
            <table>
              <tbody>
                <tr>
                  <td class="image">
                    <%block name="page_main_image"/>
                  </td>
                  <td class="description">
                    <%block name="page_main_description"/>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <%block name="page_main_main"/>
        </div>
      </div>
      <div class="page-main-footer">
        <%block name="page_main_footer"/>
      </div>
    </div>
    <div class="page-footer">
      ${pagefooter()}
      <%block name="page_footer"/>
    </div>
  </div>
  <%block name="js_footer"/>
</body>
</html>
<!--
    - vim: sts=2 sw=2 ts=2 noet
  -->
<%def name="pagefooter()">
      <div class="page-footer-content">
        <style type="text/css">
          @import "http://rakuten-ticket-static.s3.amazonaws.com/public/stylesheets/grpRakutenLinkArea.css";
          #grpRakutenLinkArea { font-size: 15px; };
        </style>
        <!-- ========== footer ========== -->
        <div id="grpRakutenLinkArea">

          <ul id="grpSpelinlk">
            <li><a href="http://ticket.rakuten.co.jp/">トップ</a></li>
            <li><a href="http://ticket.rakuten.co.jp/music">音楽</a></li>
            <li><a href="http://ticket.rakuten.co.jp/sports">スポーツ</a></li>
            <li><a href="http://ticket.rakuten.co.jp/stage">演劇</a></li>
            <li class="grpLast"><a href="http://ticket.rakuten.co.jp/event">イベント・その他</a></li>
          </ul>

          <dl id="grpKeyword">
            <dt>キーワード</dt>
            <dd>
              <ul>
                <li><a href="http://ticket.rakuten.co.jp/">チケット</a></li>
                <li><a href="http://ticket.rakuten.co.jp/stage">演劇</a></li>
                <li><a href="http://ticket.rakuten.co.jp/music">クラシック</a></li>
                <li><a href="http://ticket.rakuten.co.jp/music">コンサート</a></li>
                <li><a href="http://ticket.rakuten.co.jp/sports">野球</a></li>
                <li><a href="http://ticket.rakuten.co.jp/sports">テニス</a></li>
                <li><a href="http://ticket.rakuten.co.jp/sports">サッカー</a></li>
              </ul>
            </dd>
          </dl>

          <div id="grpFooter">
            <div id="groupServiceFooter">
              <dl class="title">
                <dt>楽天グループのサービス</dt>
                <dd class="allService"><span><a href="http://www.rakuten.co.jp/sitemap/" onclick="s.gclick('sitemap','ftr')">全サービス一覧へ</a></span></dd>
                <dd class="csr"><a href="http://corp.rakuten.co.jp/csr/" rel="nofollow"><img src="http://jp.rakuten-static.com/1/im/ci/csr/w80.gif" alt="社会的責任[CSR]" width="80" height="20" /></a></dd>
              </dl>
              <ul id="selectedService" class="serviceCol3">
                <li><dl>
                    <dt><a href="http://rental.rakuten.co.jp/" onclick="s.gclick('http://rental.rakuten.co.jp/','ftr-rel')">DVD・CDをレンタルする</a></dt>
                    <dd>楽天レンタル</dd>
                </dl></li>
                <li><dl>
                    <dt><a href="http://www.showtime.jp/isp/rakuten/" onclick="s.gclick('http://www.showtime.jp/isp/rakuten/','ftr-rel')">映画・ドラマ・スポーツ動画もっと見る</a></dt>
                    <dd>楽天VIDEO</dd>
                </dl></li>
                <li><dl>
                    <dt><a href="http://books.rakuten.co.jp/" onclick="s.gclick('http://books.rakuten.co.jp/','ftr-rel')">本・CD・DVDを購入する</a></dt>
                    <dd>楽天ブックス</dd>
                </dl></li>
                <!--
                    <li><dl>
                        <dt><a href="#########" onclick="s.gclick('#########','ftr-rel')">○○○○○○○○○○○○</a></dt>
                        <dd>○○○○○○</dd>
                    </dl></li>
                    -->
              </ul>
              <div id="serviceList">
                <dl>
                  <dt>お買物・ポイント</dt>
                  <dd><ul>
                      <li><a href="http://www.rakuten.co.jp/" onclick="s.gclick('ichiba','ftr')">ショッピング</a></li>
                      <li><a href="http://auction.rakuten.co.jp/" onclick="s.gclick('auction','ftr')">オークション</a></li>
                      <li><a href="http://books.rakuten.co.jp/" onclick="s.gclick('books','ftr')">本・DVD・CD</a></li>
                      <li><a href="http://ebook.rakuten.co.jp/" onclick="s.gclick('ebook','ftr')">電子書籍</a></li>
                      <li><a href="http://auto.rakuten.co.jp/" onclick="s.gclick('auto','ftr')">車・バイク</a></li>
                      <li><a href="https://selectgift.rakuten.co.jp/" onclick="s.gclick('gift','ftr')">セレクトギフト</a></li>

                      <li><a href="http://import.buy.com/" onclick="s.gclick('import','ftr')">個人輸入</a></li>
                      <li><a href="http://netsuper.rakuten.co.jp/" onclick="s.gclick('netsuper','ftr')">ネットスーパー</a></li>
                      <li><a href="https://my.rakuten.co.jp/" onclick="s.gclick('myrakuten','ftr')">my Rakuten</a></li>
                      <li><a href="https://point.rakuten.co.jp/" onclick="s.gclick('point','ftr')">楽天PointClub</a></li>
                      <li><a href="http://point-g.rakuten.co.jp/" onclick="s.gclick('pointgallery','ftr')">ポイント特集</a></li>
                      <li><a href="http://p-store.rakuten.co.jp/event/pointget/" onclick="s.gclick('pstore','ftr')">ポイント加盟店</a></li>
                    </ul>
                  </dd>
                </dl>
                <dl>
                  <dt>旅行・エンタメ</dt>

                  <dd><ul>
                      <li><a href="http://travel.rakuten.co.jp/" onclick="s.gclick('travel_dom','ftr')">旅行・ホテル予約・航空券</a></li>
                      <li><a href="http://gora.golf.rakuten.co.jp/" onclick="s.gclick('gora','ftr')">ゴルフ場予約</a></li>
                      <li><a href="http://ticket.rakuten.co.jp/" onclick="s.gclick('ticket','ftr')">イベント・チケット販売</a></li>
                      <li><a href="http://www.rakuteneagles.jp/" onclick="s.gclick('eagles','ftr')">楽天イーグルス</a></li>
                      <li><a href="http://rental.rakuten.co.jp/" onclick="s.gclick('rental','ftr')">DVD・CDレンタル</a></li>
                      <li><a href="http://www.showtime.jp/isp/rakuten/" onclick="s.gclick('showtime','ftr')">アニメ・映画</a></li>
                      <li><a href="http://dl.rakuten.co.jp/" onclick="s.gclick('download','ftr')">ダウンロード</a></li>
                      <li><a href="http://keiba.rakuten.co.jp/" onclick="s.gclick('keiba','ftr')">地方競馬</a></li>

                      <li><a href="http://uranai.rakuten.co.jp/" onclick="s.gclick('uranai','ftr')">占い</a></li>
                      <li><a href="https://toto.rakuten.co.jp/" onclick="s.gclick('toto','ftr')">toto・BIG</a></li>
                      <li><a href="http://entertainment.rakuten.co.jp/" onclick="s.gclick('entertainment','ftr')">映画・ドラマ・エンタメ情報</a></li>
                    </ul>
                  </dd>
                </dl>
                <dl>
                  <dt>マネー</dt>
                  <dd><ul>
                      <li><a href="https://www.rakuten-sec.co.jp/" onclick="s.gclick('sec','ftr')">ネット証券（株・FX・投資信託）</a></li>
                      <li><a href="http://www.rakuten-bank.co.jp/" onclick="s.gclick('ebank','ftr')">インターネット銀行</a></li>

                      <li><a href="http://www.rakuten-bank.co.jp/loan/cardloan/" onclick="s.gclick('ebank','ftr')">カードローン</a></li>
                      <li><a href="http://www.rakuten-card.co.jp/" onclick="s.gclick('kc','ftr')">クレジットカード</a></li>
                      <li><a href="http://www.edy.jp/">電子マネー</a></li>
                      <li><a href="http://www.rakuten-bank.co.jp/home-loan/" onclick="s.gclick('ebank','ftr')">住宅ローン</a></li>
                      <li><a href="http://hoken.rakuten.co.jp/" onclick="s.gclick('hoken','ftr')">生命保険・損害保険</a></li>
                      <li><a href="http://money.rakuten.co.jp/" onclick="s.gclick('money','ftr')">マネーサービス一覧</a></li>
                    </ul>
                  </dd>
                </dl>
                <dl>
                  <dt>暮らし・情報</dt>

                  <dd><ul>
                      <li><a href="http://www.infoseek.co.jp/" onclick="s.gclick('is','ftr')">ニュース・検索</a></li>
                      <li><a href="http://plaza.rakuten.co.jp/" onclick="s.gclick('blog','ftr')">ブログ</a></li>
                      <li><a href="http://delivery.rakuten.co.jp/" onclick="s.gclick('delivery','ftr')">出前・宅配・デリバリー</a></li>
                      <li><a href="http://dining.rakuten.co.jp/" onclick="s.gclick('dining','ftr')">グルメ・外食</a></li>
                      <li><a href="http://recipe.rakuten.co.jp" onclick="s.gclick('recipe','ftr')">レシピ</a></li>
                      <li><a href="http://www.nikki.ne.jp/" onclick="s.gclick('minshu','ftr')">就職活動</a></li>
                      <li><a href="http://career.rakuten.co.jp/" onclick="s.gclick('carrer','ftr')">仕事紹介</a></li>
                      <li><a href="http://realestate.rakuten.co.jp/"  onclick="s.gclick('is:house','ftr')">不動産情報</a></li>

                      <li><a href="http://onet.rakuten.co.jp/" onclick="s.gclick('onet','ftr')">結婚相談所</a></li>
                      <li><a href="http://wedding.rakuten.co.jp/" onclick="s.gclick('wedding','ftr')">結婚式場情報</a></li>
                      <li><a href="http://shashinkan.rakuten.co.jp/" onclick="s.gclick('shashinkan','ftr')">写真プリント</a></li>
                      <li><a href="http://nuigurumi.ynot.co.jp/" onclick="s.gclick('nuigurumi','ftr')">ぬいぐるみ電報</a></li>
                      <li><a href="http://greeting.rakuten.co.jp/" onclick="s.gclick('greeting','ftr')">グリーティングカード</a></li>
                      <li><a href="http://broadband.rakuten.co.jp/" onclick="s.gclick('broadband','ftr')">プロバイダ・インターネット接続</a></li>
                    </ul>
                  </dd>
                </dl>
                <dl>
                  <dt>ビジネス</dt>

                  <dd><ul>
                      <li><a href="http://business.rakuten.co.jp/" onclick="s.gclick('business','ftr')">ビジネス見積り</a></li>
                      <li><a href="http://research.rakuten.co.jp/" onclick="s.gclick('research','ftr')">リサーチ</a></li>
                      <li><a href="http://affiliate.rakuten.co.jp/" onclick="s.gclick('affiliate','ftr')">アフィリエイト</a></li>
                      <li><a href="http://checkout.rakuten.co.jp/biz/" onclick="s.gclick('checkout','ftr')">決済システム</a></li>
                    </ul>
                  </dd>
                </dl>
              </div><!-- /div#serviceList -->
            </div><!-- /div#groupServiceFooter -->
          </div><!-- /div#grpFooter -->
        </div><!-- /div#grpRakutenLinkArea -->

        <!-- ========== /footer ========== -->
        <div class="footernav">
          <ul>
            <li class="first"><a href="http://ticket.rakuten.co.jp/static/faq/faq.html">ヘルプ</a></li>
            <li><a href="http://www.ticketstar.jp/corporate">運営会社</a></li>
            <li><a href="https://ticket.rakuten.co.jp/contact/form">お問い合わせ</a></li>
            <li><a href="http://www.ticketstar.jp/privacy">個人情報保護方針</a></li>
            <li class="last"><a href="http://www.ticketstar.jp/legal">特定商取引法に基づく表示</a></li>
          </ul>
        </div>
        <div class="copyright">
          Copyright &copy; 2010-2011 TicketStar Inc. All Rights Reserved. 
        </div>
      </div>
</%def>

