<html lang="ja">
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
  <title>${page.title}</title>
</head>
<body bgcolor="#ffffff"><font size="1">
  <div align="center">
      <font color="red">
        
      </font>
  <img src="/static/mobile/img/logo-small.gif" width="160" height="26" alt="楽天チケット" />
  <hr size="2" noshade="noshade" color="#bf0000" />
  <br />
  <div style="background-color:#ffffbb" bgcolor="#ffffbb">
  <form action="${request.route_path("mobile_search")}" class="searchbox"><font size="3">
    &#xe691;チケット検索<br />
    <input class="text_field" type="text" name="q" value="" /><input type="submit" value="検索" />
  </font>
  <table width="100%" cellspacing="1" cellpadding="2">
    <tbody>
      <tr>
        <td bgcolor="#cccc88" width="50%" valign="center" align="center"><font size="1" color="#bf8000">&#xe67a;<a href="${request.route_path("mobile_category",category="music")}">音楽</a></font></td>
        <td bgcolor="#cccc88" width="50%" valign="center" align="center"><font size="1" color="#bf8000">&#xe653;<a href="${request.route_path("mobile_category",category="sports")}">スポーツ</a></font></td>
      </tr>
      <tr>
        <td bgcolor="#cccc88" valign="center" align="center"><font size="1" color="#bf8000">&#xe67c;<a href="${request.route_path("mobile_category",category="stage")}">演劇</a></font></td>
        <td bgcolor="#cccc88" valign="center" align="center"><font size="1" color="#bf8000">&#xe67d;<a href="${request.route_path("mobile_category",category="event")}">イベント・その他</a></font></td>
      </tr>
    </tbody>
  </table>
  </form>
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
	<img src="${h.asset.to_show_page(request,pick.mobile_image_asset)}" align="left" ${'width="%s"'% pick.mobile_image_asset.width if pick.mobile_image_asset.width else ""|} ${'height="%s"'% pick.mobile_image_asset.height if pick.mobile_image_asset.height else ""|}>
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
    <a href="http://ticket.rakuten.co.jp/static/faq/faq.html">ヘルプ</a> | <a href="http://www.ticketstar.jp/corporate">運営会社</a> | <a href="mobile/contact/form">お問い合わせ</a> | <a href="http://www.ticketstar.jp/privacy">個人情報保護方針</a> | <a href="http://www.ticketstar.jp/legal">特定商取引法に基づく表示</a>
  </div>
<div><font color="#888888">2010-2011 &copy; TicketStar, Inc. All rights reserved.</font></div>
</div>
</font>
