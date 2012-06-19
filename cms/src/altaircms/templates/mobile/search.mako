<%namespace file="./components.mako" name="co"/>

<html lang="ja">
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
  <title>楽天・ジャパン・オープン・テニス・チャンピオンシップス2012 - 楽天チケット</title>
</head>
<body bgcolor="#ffffff"><font size="1">
  <div align="center">
      <font color="red">
        
      </font>
	  <a href="${request.route_path("mobile_index")}"><font color="#bf0000" size="3"><img src="/static/mobile/img/logo-small.gif" alt="楽天チケット" width="160" height="26"></font></a>
  <hr color="#bf0000" size="1" noshade="noshade">
</div>
<div>

## breadcrumbs
${breadcrumbs}
    <div style="background-image: url(&quot;/static/mobile/img/bg_bar.gif&quot;); background-color: rgb(191, 0, 0);" bgcolor="#bf0000" background="/static/mobile/img/bg_bar.gif"><font color="#ffffff" size="3"><font color="#ffbf00">■</font>検索結果</font>
</div></div>

##
<div align="center">
『${freeword}』を含む公演
</div>
<div>
%for c, qs in classifieds:
  ${synonym.get(c.name,c.label)}(${qs.count()})
%endfor
</div>

<div>
<hr color="#bf0000" size="1" noshade="noshade">
%if pagesets.count() <= 0:
  <p>キーワードに該当する公演は見つかりませんでした。</p>
  <p>下記のことをお試しください。</p>
  ・絞り込むカテゴリを変えてください。<br>
  ・検索キーワードを変えてください。<br>
%else:
  ${pagesets.count()}件見つかりました。<br>
  <hr color="#bf0000" size="1" noshade="noshade">

  <%
seq = h.paginate(request,pagesets, item_count=pagesets.count())
%>

${seq.pager()}
  %for pageset in seq.paginated():

  <% event = pageset.event %>

	%if event:
	  <a href="${h.mobilelink.to_publish_page_from_pageset(request,pageset)}">${pageset.name}</a><br>
	  ${h.base.jterm(event.event_open,event.event_close)}<br>
	  ${event.title}<br>
	  一般: ${h.base.jdate_with_hour(event.deal_open)}<br>
	   <hr color="#bf0000" size="1" noshade="noshade">
	%endif
  %endfor
${seq.pager()}
%endif

<div style="background-color: rgb(255, 255, 187);" bgcolor="#ffffbb" align="center">
 ${co.search_form(request)}
 </div>
<hr color="#888888" size="1" noshade="noshade">
<div align="center">
  <div>
    <a href="http://ticket.rakuten.co.jp/static/faq/faq.html">ヘルプ</a> | <a href="http://www.ticketstar.jp/corporate">運営会社</a> | <a href="contact/form">お問い合わせ</a> | <a href="http://www.ticketstar.jp/privacy">個人情報保護方針</a> | <a href="http://www.ticketstar.jp/legal">特定商取引法に基づく表示</a>
  </div>
<div><font color="#888888">2010-2011 © TicketStar, Inc. All rights reserved.</font></div>
</div>
</font></body>
</html>


