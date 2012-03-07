<%inherit file="base.mako"/>

<%block name="meta">
  ${self.inherits.meta()}
  <meta name="description" content="松下奈緒コンサートツアー2012　for meの公演についての詳細、チケット予約">
  <meta name="keywords" content="チケット,演劇,クラシック,オペラ,コンサート,バレエ,ミュージカル,野球,サッカー,格闘技">
</%block>

<%block name="title">
松下奈緒コンサートツアー2012　for me - 楽天チケット
</%block>

<%block name="css_prerender">
  ${self.inherits.css_prerender()}
  <link rel="stylesheet" type="text/css" href="http://rakuten-ticket-static.s3.amazonaws.com/public/stylesheets/default.css" />
  <link rel="stylesheet" type="text/css" href="http://rakuten-ticket-static.s3.amazonaws.com/public/stylesheets/ui-lightness/jquery-ui-1.8.13.custom.css" />
  <link rel="stylesheet" type="text/css" href="http://rakuten-ticket-static.s3.amazonaws.com/public/stylesheets/order.css" />
</%block>

<%block name="js_prerender">
  ${self.inherits.js_prerender()}
  <script type="text/javascript">
    var _tscn = 'ts93c91afd';
    (function(d,x,n,s){n=d.createElement('script'),n.type='text/javascript',n.src=x,n.async=true;s=d.getElementsByTagName("script")[0];s.parentNode.insertBefore(n,s);})(document,'https://secure.ticketstar.jp/-/b.js');
</script>
  <script type="text/javascript" src="http://rakuten-ticket-static.s3.amazonaws.com/public/javascripts/jquery-1.6.1.min.js"></script>
  <script type="text/javascript" src="http://rakuten-ticket-static.s3.amazonaws.com/public/javascripts/jquery-ui-1.8.13.custom.min.js"></script>
</%block>


<%block name="page_header_content">
    <div class="logo_and_globalnav">
      <div class="logo">
        <a href="http://www.rakuten.co.jp/" title="楽天" class="rakuten">楽天</a>
        <a href="http://ticket.rakuten.co.jp/" title="チケット" class="ticket">チケット</a>
      </div>
      <div class="tagline">
        <ul>
          <li class="first">チケット販売・イベント予約</li>
          <li id="grpNote">
            <noscript>
              <a href="https://card.rakuten.co.jp/entry/">今すぐ2,000ポイント！</a>
            </noscript>
            <script type="text/javascript" src="http://jp.rakuten-static.com/1/js/lib/prm_selector.js"></script>
            <script type="text/javascript" src="http://jp.rakuten-static.com/1/js/grp/hdr/prm_sender.js"></script>
          </li>
          <li class="last"><a href="http://www.rakuten.co.jp/">楽天市場へ</a></li>
        </ul>
      </div>
      <div class="globalnav">
        <ul>
          <li class="first"><a href="http://ticket.rakuten.co.jp/static/info_top.html">初めての方へ</a></li>
          <li><a href="http://ticket.rakuten.co.jp/static/stop.html">公演中止・変更情報</a></li>
          <li><a href="http://ticket.rakuten.co.jp/static/faq/faq.html">ヘルプ</a></li>
          <li class="last"><a href="http://ticket.rakuten.co.jp/static/sitemap.html">サイトマップ</a></li>
        </ul>
      </div>
    </div>
    <div class="Rnavbar">
      <ul>
        <li class="first last"><a href="http://ticket.rakuten.co.jp/" class="top">チケットトップ</a></li>
      </ul>
    </div>
    <div class="navbar_and_search">
      <form action="http://ticket.rakuten.co.jp/s/" class="searchbox">
        <input class="text_field" type="text" name="q" value="" />
        <input class="submit" type="submit" value="検索" src="http://rakuten-ticket-static.s3.amazonaws.com/public/images/search_btn_bg.gif" />
      </form>
      <ul class="navbar">
        <li class="first"><a href="http://ticket.rakuten.co.jp/music">音楽</a></li>
        <li><a href="http://ticket.rakuten.co.jp/sports">スポーツ</a></li>
        <li><a href="http://ticket.rakuten.co.jp/stage">演劇</a></li>
        <li class="last"><a href="http://ticket.rakuten.co.jp/event">イベント・その他</a></li>
      </ul>
    </div>
</%block>

<%block name="notice">
</%block>

<%block name="page_main_header">
      <div class="page-main-header">
        <div class="page-main-header-content"></div>
      </div>

</%block>
<%block name="page_main_main">
      <div class="page-main-main">
        <div class="page-main-main-content">
          <h1 class="title" style="float: left;">松下奈緒コンサートツアー2012　for me</h1>
          <div id="social"  style="float: right; padding-top: 10px">
            <a href="http://twitter.com/share" class="twitter-share-button" data-count="none" data-via="RakutenTicket" data-lang="ja">ツイート</a><script type="text/javascript" src="http://platform.twitter.com/widgets.js"></script>
            <iframe src="http://www.facebook.com/plugins/like.php?app_id=233610706676154&amp;href=http%3A%2F%2Fticket.rakuten.co.jp%2Fs%2F%25E9%259F%25B3%25E6%25A5%25BD%2F%25E6%259D%25BE%25E4%25B8%258B%25E5%25A5%2588%25E7%25B7%2592%25E3%2582%25B3%25E3%2583%25B3%25E3%2582%25B5%25E3%2583%25BC%25E3%2583%2588%25E3%2583%2584%25E3%2582%25A2%25E3%2583%25BC2012%25E3%2580%2580for%2Bme%2F%21SCMNF&amp;send=false&amp;layout=button_count&amp;width=100&amp;show_faces=false&amp;action=like&amp;colorscheme=light&amp;font&amp;height=20" scrolling="no" frameborder="0" style="border:none; overflow:hidden; width:100px; height:20px;" allowTransparency="true"></iframe>
          </div>
          <div class="description_and_image">
            <table>
              <tbody>
                <tr>
                  <td class="image">
                    <img src="http://rakuten-ticket-static.s3-ap-northeast-1.amazonaws.com/images/uploaded/fd41fbb6-086f-41e4-84ba-b483987a937f.jpg" />
                  </td>
                  <td class="description">
                    <div style="TEXT-ALIGN: center"><font face="Arial, Verdana"><b><br></b></font></div>
                    <div style="TEXT-ALIGN: center"><font size="3" face="Arial, Verdana"><b>アイフルホーム presents</b></font></div>
                    <div style="TEXT-ALIGN: center"><strong><font size="3"></font></strong>&nbsp;</div><font face="Arial, Verdana">
                      <div style="TEXT-ALIGN: center"><b><font size="4">松下奈緒コンサートツアー2012　for me</font></b></div>
                      <div style="TEXT-ALIGN: center"><font size="4"></font>&nbsp;</div></font>
                    <div style="TEXT-ALIGN: center"><font size="3" face="Arial, Verdana"><b>supported by ＪＡバンク</b></font></div>
                    <div style="TEXT-ALIGN: center"><strong><font size="4"></font></strong>&nbsp;</div>
                    <div style="TEXT-ALIGN: center"><strong><font size="4"></font></strong>&nbsp;</div>
                    <div style="TEXT-ALIGN: center">&nbsp;</div>
                    <div style="TEXT-ALIGN: center" align="left"><strong>【公演日時・会場】</strong></div>
                    <div style="TEXT-ALIGN: center" align="left">&nbsp;</div><font face="Arial, Verdana"><b>
                        <div style="TEXT-ALIGN: center"><font size="1">2012年6月3日（日）　16:30開場／17:00開演　岸和田市立浪切ホール　大ホール</font></div>
                        <div style="TEXT-ALIGN: center"><font size="1">2012年7月16日（月・祝）　16:30開場／17:00開演　神戸国際会館こくさいホール<br></font></div></b></font>
                    <div style="TEXT-ALIGN: left"><font face="Arial, Verdana"><b><br></b></font></div>
                    <div style="TEXT-ALIGN: left"><font face="Arial, Verdana"><b><br></b></font></div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="summary">
            <dl>
              <dt>公演期間</dt>
              <dd>2012年6月3日〜2012年7月16日 (<a href="!SCMNF#performance-calendar">公演カレンダーを見る</a>)</dd>
              <dt class="notice">説明／注意事項</dt>
              <dd>※未就学児童のご入場はお断りいたします。</dd>
              <dt class="seats_and_prices">料金</dt>
              <dd><table style="WIDTH: 128pt; BORDER-COLLAPSE: collapse" border="0" cellspacing="0" cellpadding="0" width="170">
                  <colgroup>
                    <col style="WIDTH: 65pt; mso-width-source: userset; mso-width-alt: 2752" width="86">
                    <col style="WIDTH: 63pt; mso-width-source: userset; mso-width-alt: 2688" width="84">
                  </colgroup><tbody>
                    <tr style="HEIGHT: 13.5pt" height="18">
                      <td style="BORDER-BOTTOM: windowtext 0.5pt solid; BORDER-LEFT: windowtext 0.5pt solid; BACKGROUND-COLOR: #bfbfbf; WIDTH: 65pt; HEIGHT: 13.5pt; BORDER-TOP: windowtext 0.5pt solid; BORDER-RIGHT: windowtext 0.5pt solid" class="xl65" height="18" width="86"><font size="3" face="ＭＳ Ｐゴシック">席種</font></td>
                      <td style="BORDER-BOTTOM: windowtext 0.5pt solid; BORDER-LEFT: windowtext; BACKGROUND-COLOR: #bfbfbf; WIDTH: 63pt; BORDER-TOP: windowtext 0.5pt solid; BORDER-RIGHT: windowtext 0.5pt solid" class="xl65" width="84"><font size="3" face="ＭＳ Ｐゴシック">料金</font></td></tr>
                    <tr style="HEIGHT: 18.75pt; mso-height-source: userset" height="25">
                      <td style="BORDER-BOTTOM: windowtext 0.5pt solid; BORDER-LEFT: windowtext 0.5pt solid; BACKGROUND-COLOR: transparent; HEIGHT: 18.75pt; BORDER-TOP: windowtext; BORDER-RIGHT: windowtext 0.5pt solid" class="xl63" height="25"><font size="3" face="ＭＳ Ｐゴシック">全席指定</font></td>
                      <td style="BORDER-BOTTOM: windowtext 0.5pt solid; BORDER-LEFT: windowtext; BACKGROUND-COLOR: transparent; BORDER-TOP: windowtext; BORDER-RIGHT: windowtext 0.5pt solid" class="xl64" align="right"><font size="3" face="ＭＳ Ｐゴシック">¥6,300</font></td></tr></tbody></table></dd>
              <dt class="contact">お問い合わせ先</dt>
              <dd><div>【お問合せ】</div><div>サウンドクリエーター　06-6357-4400 / www.sound-c.co.jp</div><div>≪浪切公演≫浪切ホールチケットカウンター　072-439-4915 / www.namikiri.jp</div><div>≪神戸公演≫神戸国際会館　078-231-8162 / www.kih.co.jp</div><div><br></div></dd>
              <dt class="sales_period">販売期間</dt>
              <dd>
                <dl class="sales_segments">
                  <dt><img src="http://rakuten-ticket-static.s3.amazonaws.com/public/images/icon_general.gif" alt="一般販売" /></dt>
                  <dd>
                    2012年3月3日(土)〜7月12日(木)
                  </dd>
                </dl>
              </dd>
            </dl>
          </div>
          <div class="performances">
            <form>
              <div class="fields">
                <div class="field">
                  <input type="checkbox" id="form-showUnavailablePerformances"><label for="form-showUnavailablePerformances">販売終了した公演も表示</label>
                </div>
              </div>
            </form>
            <table>
              <thead>
                <tr>
                  <th class="serial">&nbsp;</th>
                  <th class="performance_name">公演名</th>
                  <th class="performance_period">公演日時</th>
                  <th class="venue">会場</th>
                  <th class="action">&nbsp;</th>
                </tr>
              </thead>
              <tbody>
                <tr id="performance-1">
                  <td class="serial">
                    <span class="serial">1</span>
                  </td>
                  <td class="performance_name">
                    松下奈緒コンサートツアー2012　for me
                  </td>
                  <td class="performance_period">
                    <span class="date">2012年6月3日(日) 17:00</span>
                  </td>
                  <td class="venue">
                    岸和田市立浪切ホール 大ホール
                  </td>
                  <td class="action">
                    <a href="https://www.e-get.jp/tstar/pt/&amp;s=SCMNF0603" class="button reserve_or_order button-reserve_or_order">予約・購入</a>
                  </td>
                </tr>
                <tr id="performance-2">
                  <td class="serial">
                    <span class="serial">2</span>
                  </td>
                  <td class="performance_name">
                    松下奈緒コンサートツアー2012　for me
                  </td>
                  <td class="performance_period">
                    <span class="date">2012年7月16日(月) 17:00</span>
                  </td>
                  <td class="venue">
                    神戸国際会館　こくさいホール
                  </td>
                  <td class="action">
                    <a href="https://www.e-get.jp/tstar/pt/&amp;s=SCMNF0716" class="button reserve_or_order button-reserve_or_order">予約・購入</a>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <script type="text/javascript">
            function onShowUnavailablePerformancesChange() {
            var n = $(".performances tr.unavailable");
            if ($(this).attr("checked"))
            n.removeClass("hide");
            else
            n.addClass("hide");
            }
            $("#form-showUnavailablePerformances").change(onShowUnavailablePerformancesChange);
            onShowUnavailablePerformancesChange();
          </script>
          <div class="calendar" id="performance-calendar">
            <table>
              <thead>
                <tr>
                  <td class="empty"></td>
                  <th class="first">月</th>
                  <th>火</th>
                  <th>水</th>
                  <th>木</th>
                  <th>金</th>
                  <th>土</th>
                  <th class="last">日</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <th class="month">
                    <span class="month-header"><span class="month-header-content"></span></span>
                    <span class="month-main">6月</span>
                    <span class="month-footer"><span class="month-footer-content"></span></span>
                  </th>
                  <td class="first odd_month ">
                    <span class="day">28</span>
                    <ul>
                    </ul>
                  </td>
                  <td class=" odd_month ">
                    <span class="day">29</span>
                    <ul>
                    </ul>
                  </td>
                  <td class=" odd_month ">
                    <span class="day">30</span>
                    <ul>
                    </ul>
                  </td>
                  <td class=" odd_month ">
                    <span class="day">31</span>
                    <ul>
                    </ul>
                  </td>
                  <td class=" even_month ">
                    <span class="day">1</span>
                    <ul>
                    </ul>
                  </td>
                  <td class=" even_month saturday">
                    <span class="day">2</span>
                    <ul>
                    </ul>
                  </td>
                  <td class="last holiday even_month ">
                    <span class="day">3</span>
                    <ul>
                      <li><span class="serial"><a href="!SCMNF#performance-1">1</a></span>
                        <a href="https://www.e-get.jp/tstar/pt/&amp;s=SCMNF0603" target="_blank">17:00</a></li>
                    </ul>
                  </td>
                </tr>
                <tr>
                  <td class="empty"></td>
                  <td class="first even_month ">
                    <span class="day">4</span>
                    <ul>
                    </ul>
                  </td>
                  <td class=" even_month ">
                    <span class="day">5</span>
                    <ul>
                    </ul>
                  </td>
                  <td class=" even_month ">
                    <span class="day">6</span>
                    <ul>
                    </ul>
                  </td>
                  <td class=" even_month ">
                    <span class="day">7</span>
                    <ul>
                    </ul>
                  </td>
                  <td class=" even_month ">
                    <span class="day">8</span>
                    <ul>
                    </ul>
                  </td>
                  <td class=" even_month saturday">
                    <span class="day">9</span>
                    <ul>
                    </ul>
                  </td>
                  <td class="last holiday even_month ">
                    <span class="day">10</span>
                    <ul>
                    </ul>
                  </td>
                </tr>
                <tr>
                  <td class="empty"></td>
                  <td class="first even_month ">
                    <span class="day">11</span>
                    <ul>
                    </ul>
                  </td>
                  <td class=" even_month ">
                    <span class="day">12</span>
                    <ul>
                    </ul>
                  </td>
                  <td class=" even_month ">
                    <span class="day">13</span>
                    <ul>
                    </ul>
                  </td>
                  <td class=" even_month ">
                    <span class="day">14</span>
                    <ul>
                    </ul>
                  </td>
                  <td class=" even_month ">
                    <span class="day">15</span>
                    <ul>
                    </ul>
                  </td>
                  <td class=" even_month saturday">
                    <span class="day">16</span>
                    <ul>
                    </ul>
                  </td>
                  <td class="last holiday even_month ">
                    <span class="day">17</span>
                    <ul>
                    </ul>
                  </td>
                </tr>
                <tr>
                  <td class="empty"></td>
                  <td class="first even_month ">
                    <span class="day">18</span>
                    <ul>
                    </ul>
                  </td>
                  <td class=" even_month ">
                    <span class="day">19</span>
                    <ul>
                    </ul>
                  </td>
                  <td class=" even_month ">
                    <span class="day">20</span>
                    <ul>
                    </ul>
                  </td>
                  <td class=" even_month ">
                    <span class="day">21</span>
                    <ul>
                    </ul>
                  </td>
                  <td class=" even_month ">
                    <span class="day">22</span>
                    <ul>
                    </ul>
                  </td>
                  <td class=" even_month saturday">
                    <span class="day">23</span>
                    <ul>
                    </ul>
                  </td>
                  <td class="last holiday even_month ">
                    <span class="day">24</span>
                    <ul>
                    </ul>
                  </td>
                </tr>
                <tr>
                  <th class="month">
                    <span class="month-header"><span class="month-header-content"></span></span>
                    <span class="month-main">7月</span>
                    <span class="month-footer"><span class="month-footer-content"></span></span>
                  </th>
                  <td class="first even_month ">
                    <span class="day">25</span>
                    <ul>
                    </ul>
                  </td>
                  <td class=" even_month ">
                    <span class="day">26</span>
                    <ul>
                    </ul>
                  </td>
                  <td class=" even_month ">
                    <span class="day">27</span>
                    <ul>
                    </ul>
                  </td>
                  <td class=" even_month ">
                    <span class="day">28</span>
                    <ul>
                    </ul>
                  </td>
                  <td class=" even_month ">
                    <span class="day">29</span>
                    <ul>
                    </ul>
                  </td>
                  <td class=" even_month saturday">
                    <span class="day">30</span>
                    <ul>
                    </ul>
                  </td>
                  <td class="last holiday odd_month ">
                    <span class="day">1</span>
                    <ul>
                    </ul>
                  </td>
                </tr>
                <tr>
                  <td class="empty"></td>
                  <td class="first odd_month ">
                    <span class="day">2</span>
                    <ul>
                    </ul>
                  </td>
                  <td class=" odd_month ">
                    <span class="day">3</span>
                    <ul>
                    </ul>
                  </td>
                  <td class=" odd_month ">
                    <span class="day">4</span>
                    <ul>
                    </ul>
                  </td>
                  <td class=" odd_month ">
                    <span class="day">5</span>
                    <ul>
                    </ul>
                  </td>
                  <td class=" odd_month ">
                    <span class="day">6</span>
                    <ul>
                    </ul>
                  </td>
                  <td class=" odd_month saturday">
                    <span class="day">7</span>
                    <ul>
                    </ul>
                  </td>
                  <td class="last holiday odd_month ">
                    <span class="day">8</span>
                    <ul>
                    </ul>
                  </td>
                </tr>
                <tr>
                  <td class="empty"></td>
                  <td class="first odd_month ">
                    <span class="day">9</span>
                    <ul>
                    </ul>
                  </td>
                  <td class=" odd_month ">
                    <span class="day">10</span>
                    <ul>
                    </ul>
                  </td>
                  <td class=" odd_month ">
                    <span class="day">11</span>
                    <ul>
                    </ul>
                  </td>
                  <td class=" odd_month ">
                    <span class="day">12</span>
                    <ul>
                    </ul>
                  </td>
                  <td class=" odd_month ">
                    <span class="day">13</span>
                    <ul>
                    </ul>
                  </td>
                  <td class=" odd_month saturday">
                    <span class="day">14</span>
                    <ul>
                    </ul>
                  </td>
                  <td class="last holiday odd_month ">
                    <span class="day">15</span>
                    <ul>
                    </ul>
                  </td>
                </tr>
                <tr class="last">
                  <td class="empty"></td>
                  <td class="first odd_month ">
                    <span class="day">16</span>
                    <ul>
                      <li><span class="serial"><a href="!SCMNF#performance-2">2</a></span>
                        <a href="https://www.e-get.jp/tstar/pt/&amp;s=SCMNF0716" target="_blank">17:00</a></li>
                    </ul>
                  </td>
                  <td class=" odd_month ">
                    <span class="day">17</span>
                    <ul>
                    </ul>
                  </td>
                  <td class=" odd_month ">
                    <span class="day">18</span>
                    <ul>
                    </ul>
                  </td>
                  <td class=" odd_month ">
                    <span class="day">19</span>
                    <ul>
                    </ul>
                  </td>
                  <td class=" odd_month ">
                    <span class="day">20</span>
                    <ul>
                    </ul>
                  </td>
                  <td class=" odd_month saturday">
                    <span class="day">21</span>
                    <ul>
                    </ul>
                  </td>
                  <td class="last holiday odd_month ">
                    <span class="day">22</span>
                    <ul>
                    </ul>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <br style="clear: all"/>
          <script type="text/javascript">
            (function() {
            var selectedNode = null;
            function select(url) {
            var g = /#([a-zA-Z0-9_-]+)/.exec(url);
            if (g) {
            var newlySelectedNode = $(document.getElementById(g[1]));
            if (selectedNode)
            selectedNode.removeClass("selected");
            newlySelectedNode.addClass("selected");
            selectedNode = newlySelectedNode;
            }
            }
            $("a").click(function(e) { select(this.getAttribute('href')) });
            $(function(){ select(location.hash) });
            })();
          </script>

        </div>
      </div>
</%block>

<%block name="page_main_footer">
      <div class="page-main-footer">
        <div class="page-main-footer-content"></div>
      </div>
</%block>

<%block name="page_footer">
  ${self.inherits.page_footer()}
</%block>

<%block name="js_footer">
  ${self.inherits.js_footer()}
  <script type="text/javascript">
    if("http:" == document.location.protocol) {
    document.write(unescape("%3Cimg src='http://grp02.trc.ashiato.rakuten.co.jp/svc-ashiato/trc?service_id=19'%3E"))
    }
    var _gaq = _gaq || [];_gaq.push(['_setAccount', 'UA-336834-1']);_gaq.push(['_trackPageview']);(function() { var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js'; var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);})();
  </script>
</%block>

### 
<%doc>
<%block name="@">
  ${self.inherits.@()}
</%block>
</%doc>
