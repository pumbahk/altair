<%def name="widgets(name)">
  % for w in display_blocks[name]:
      ${w|n}
  % endfor
</%def>

<html lang="ja">
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
  <title>${page.title}</title>
</head>
<body bgcolor="#ffffff"><font size="1">
  <div align="center">
      <font color="red">
        
      </font>
  <img src="http://rakuten-ticket-static.s3.amazonaws.com/public/images/mobile/logo-small.gif" width="160" height="26" alt="楽天チケット" />
  <hr size="2" noshade="noshade" color="#bf0000" />
  <br />
  <div style="background-color:#ffffbb" bgcolor="#ffffbb">
  <form action="${request.route_path("mobile_page_search")}" class="searchbox"><font size="3">
    &#xe691;チケット検索<br />
    <input class="text_field" type="text" name="q" value="" /><input type="submit" value="検索" />
  </font>
  <table width="100%" cellspacing="1" cellpadding="2">
    <tbody>
      <tr>
        <td bgcolor="#cccc88" width="50%" valign="center" align="center"><font size="1" color="#bf8000">&#xe67a;<a href="mobile/music">音楽</a></font></td>
        <td bgcolor="#cccc88" width="50%" valign="center" align="center"><font size="1" color="#bf8000">&#xe653;<a href="mobile/sports">スポーツ</a></font></td>
      </tr>
      <tr>
        <td bgcolor="#cccc88" valign="center" align="center"><font size="1" color="#bf8000">&#xe67c;<a href="mobile/stage">演劇</a></font></td>
        <td bgcolor="#cccc88" valign="center" align="center"><font size="1" color="#bf8000">&#xe67d;<a href="mobile/event">イベント・その他</a></font></td>
      </tr>
    </tbody>
  </table>
  </form>
  </div>
</div>
<div>

<div style="background-image:url(http://rakuten-ticket-static.s3.amazonaws.com/public/images/mobile/bg_bar.gif);background-color:#bf0000" bgcolor="#bf0000" background="http://rakuten-ticket-static.s3.amazonaws.com/public/images/mobile/bg_bar.gif"><font color="#ffffff" size="3"><font color="#ffbf00">■</font>トピックス</font></div>
  <img src="http://rakuten-ticket-static.s3.amazonaws.com/public/images/mobile/new.gif" width="23" height="8" />
      <a href="http://ticket.rakuten.co.jp/static/features/kingtut/?top">70万人突破目前！ツタンカーメン展。大阪会場は7/16まで。東京会場は8/4開幕！</a>
      <br />
  <img src="http://rakuten-ticket-static.s3.amazonaws.com/public/images/mobile/new.gif" width="23" height="8" />
      <a href="static/features/rakutenopen/index.html?top">6/10（日）10時発売開始！今年も世界の強豪が来日！楽天ジャパンオープン2012</a>
      <br />
  <img src="http://rakuten-ticket-static.s3.amazonaws.com/public/images/mobile/new.gif" width="23" height="8" />
      <a href="static/features/tube/index.html?top">TUBE野外ライブを楽チケで購入すると、メンバーサイン入りタオルをプレゼント！</a>
      <br />
</div>
        
<div>
  <div style="background-image:url(http://rakuten-ticket-static.s3.amazonaws.com/public/images/mobile/bg_bar.gif);background-color:#bf0000" bgcolor="#bf0000" background="http://rakuten-ticket-static.s3.amazonaws.com/public/images/mobile/bg_bar.gif"><font color="#ffffff" size="3"><font color="#ffbf00">■</font>おすすめ</font></div>
      <img src="http://rakuten-ticket-static.s3-ap-northeast-1.amazonaws.com/images/uploaded/cdde1f60-9529-4c54-91e3-780b0c35080d.jpg" align="left" width="{$pickItem.mobileImage.width}" height="{$pickItem.mobileImage.height}">
      <a href="static/features/rakutenopen/index.html?top">楽天・ジャパン・オープン・テニス・チャンピオンシップス2012</a>
       <br clear="all" style="clear:both" />
      <img src="http://rakuten-ticket-static.s3-ap-northeast-1.amazonaws.com/images/uploaded/62e3fcee-143c-48fb-9676-6b0345c281f7.jpg" align="left" width="{$pickItem.mobileImage.width}" height="{$pickItem.mobileImage.height}">
      <a href="s/259Fウ讌ス/2581%259D2581ョ莉%2596/LOVE-1+FESTIVAL+SEASON+2/!KMLFS">LOVE-1 FESTIVAL SEASON 2</a>
       <br clear="all" style="clear:both" />
      <img src="http://rakuten-ticket-static.s3-ap-northeast-1.amazonaws.com/images/uploaded/c5da9ff3-fd88-458c-9ae6-5c452df9ebe2.jpg" align="left" width="{$pickItem.mobileImage.width}" height="{$pickItem.mobileImage.height}">
      <a href="static/features/tube/index.html?event">TUBE ROUND SPECIAL 2012</a>
       <br clear="all" style="clear:both" />
      <img src="http://rakuten-ticket-static.s3-ap-northeast-1.amazonaws.com/images/uploaded/bdda4878-49e5-4803-bce9-53c130f2cc64.jpg" align="left" width="{$pickItem.mobileImage.width}" height="{$pickItem.mobileImage.height}">
      <a href="s/薀259F恰ソ/礇2582%2583❼%2582激%2583%25832582ッ/2583%2587礇2582ｃ%2582冴%2583%258B礇2583若%2583祉%2582⒢%2583潟%2583祉%2582%2583❼%2582激%2583%25832582ッ+2580%259C礇2581障%2581祉%2581%25862581ョ螟%259C礇2581㍼%259F恰ソ篌%259A+2012+Dreams+Come+True/!SPDMD">ディズニー・オン・クラシック 〜まほうの夜の音楽会 2012 Dreams Come True</a>
       <br clear="all" style="clear:both" />
      <img src="http://rakuten-ticket-static.s3-ap-northeast-1.amazonaws.com/images/uploaded/b2b4b220-fca1-45d2-b74f-a6e8e23ef1cb.jpg" align="left" width="{$pickItem.mobileImage.width}" height="{$pickItem.mobileImage.height}">
      <a href="s/!SCSMS">サンドウィッチマン ライブツアー2012《先行販売》</a>
       <br clear="all" style="clear:both" />
      <img src="http://rakuten-ticket-static.s3-ap-northeast-1.amazonaws.com/images/uploaded/e697f052-a498-468f-a4d3-339d0a03203d.jpg" align="left" width="{$pickItem.mobileImage.width}" height="{$pickItem.mobileImage.height}">
      <a href="s/礇2582ゃ%2583%2599礇2583潟%2583%2588/礇2583%2596礇2583❼%2582鴻%2583%2588鐚%2581鐚%2592鐚%2590鐚%2591鐚%2592鐚%2588筝㊤%259B遵%259C井%2596鴻%2583私259D蟾%259E絅259C井%2596鴻%2583紙2596邵%2584鐚%2589/!KNBLS">ブラスト！２０１２（中国・九州・沖縄）</a>
       <br clear="all" style="clear:both" />
      <img src="http://rakuten-ticket-static.s3-ap-northeast-1.amazonaws.com/images/uploaded/da3d1ace-b545-47a3-b03f-56f5e5905414.jpg" align="left" width="{$pickItem.mobileImage.width}" height="{$pickItem.mobileImage.height}">
      <a href="s/2594絅258A%2587礇2583祉%2583%259F礇2583ャ%2583若%2582吾%2582%2583貍%2594258A%2587/2598%258E豐サ蠎ァ2589オ讌ュ1402591ィ蟷エ險%2598蠢オ+258C%2597絣銀2589薀2583%258E腑2589劫%2588ュ%25852594/!MJKSK">譏取イサ蠎ァ蜑オ讌ュ140蜻ィ蟷エ險伜ソオ 蛹怜ウカ荳蛾ヮ迚ケ蛻・蜈ャ貍/a>
       <br clear="all" style="clear:both" />
      <img src="http://rakuten-ticket-static.s3-ap-northeast-1.amazonaws.com/images/uploaded/f408bc44-ea51-4810-853d-078779879fbe.jpg" align="left" width="{$pickItem.mobileImage.width}" height="{$pickItem.mobileImage.height}">
      <a href="mobile/ticket.rakuten.co.jp/s/!RY6RE">楽天イーグルス</a>
       <br clear="all" style="clear:both" />
  </div>

<hr size="1" color="#888888" noshade="noshade" />
<div align="center">
  <div>
    <a href="http://ticket.rakuten.co.jp/static/faq/faq.html">ヘルプ</a> | <a href="http://www.ticketstar.jp/corporate">運営会社</a> | <a href="mobile/contact/form">お問い合わせ</a> | <a href="http://www.ticketstar.jp/privacy">個人情報保護方針</a> | <a href="http://www.ticketstar.jp/legal">特定商取引法に基づく表示</a>
  </div>
<div><font color="#888888">2010-2011 &copy; TicketStar, Inc. All rights reserved.</font></div>
</div>
</font>
