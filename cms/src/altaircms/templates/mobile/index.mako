<%namespace file="./components.mako" name="co"/>

<html lang="ja">
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
  <title>チケット販売・イベントの予約 [音楽 / コンサート / 舞台 / スポーツ] - 楽天チケット</title>
</head>
<body bgcolor="#ffffff"><font size="1">
  <div align="center">
      <font color="red">
        
      </font>
  <img src="/static/mobile/img/logo-small.gif" width="160" height="26" alt="楽天チケット" />
  <hr size="2" noshade="noshade" color="#bf0000" />
  <br />
  <div style="background-color:#ffffbb" bgcolor="#ffffbb">
    ${co.index_search_form(request)}
  </div>
</div>
<div>

<div style="background-image:url(/static/mobile/img/bg_bar.gif);background-color:#bf0000" bgcolor="#bf0000" background="/static/mobile/img/bg_bar.gif"><font color="#ffffff" size="3"><font color="#ffbf00">■</font>トピックス</font></div>
%for topic in topics:
  <img src="/static/mobile/img/new.gif" width="23" height="8" />
      <a href="${h.mobilelink.get_link_from_topic(request,topic)}">${topic.title}</a>
     <br />
%endfor
</div>

%if picks.count() > 0:
  <div style="background-image:url(/static/mobile/img/bg_bar.gif);background-color:#bf0000" bgcolor="#bf0000" background="/static/mobile/img/bg_bar.gif"><font color="#ffffff" size="3"><font color="#ffbf00">■</font>おすすめ</font></div>
  %for pick in picks:
    ${h.asset.create_show_img(request,pick.mobile_image_asset,align="left")}
  <% url= h.mobilelink.get_link_from_topcontent(request,pick)%>
	%if url == "":
	  ${pick.title}
	%else:
	  <a href="${h.mobilelink.get_link_from_topcontent(request,pick)}">${pick.title}</a>
	%endif
  <br clear="all" style="clear:both" />
  %endfor 
%endif
</div>


<hr size="1" color="#888888" noshade="noshade" />
<div align="center">
  <div>
    <a href="${h.mobilelink.static_page(request,"faq/faq")}">ヘルプ</a> | <a href="http://www.ticketstar.jp/corporate">運営会社</a> | <a href="mobile/contact/form">お問い合わせ</a> | <a href="http://www.ticketstar.jp/privacy">個人情報保護方針</a> | <a href="http://www.ticketstar.jp/legal">特定商取引法に基づく表示</a>
  </div>
<div><font color="#888888">2010-2011 &copy; TicketStar, Inc. All rights reserved.</font></div>
</div>
<hr size="1" color="#888888" noshade="noshade" />
<div align="center">
  <div>
    <a href="http://ticket.rakuten.co.jp/static/faq/faq.html">ヘルプ</a> | <a href="http://www.ticketstar.jp/corporate">運営会社</a> | <a href="mobile/contact/form">お問い合わせ</a> | <a href="http://www.ticketstar.jp/privacy">個人情報保護方針</a> | <a href="http://www.ticketstar.jp/legal">特定商取引法に基づく表示</a>
  </div>
<div><font color="#888888">2010-2011 &copy; TicketStar, Inc. All rights reserved.</font></div>
</div>
</body>
</html>
