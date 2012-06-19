<html lang="ja">
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
  <title>${page.title}</title>
  ##<title>楽天・ジャパン・オープン・テニス・チャンピオンシップス2012 - 楽天チケット</title>
</head>
<body bgcolor="#ffffff"><font size="1">
  <div align="center">
      <font color="red">
        
      </font>
  <a href="${request.route_path("mobile_index")}"><font size="3" color="#bf0000"><img src="/static/mobile/img/logo-small.gif" width="160" height="26" alt="楽天チケット" /></font></a>
  <hr size="1" noshade="noshade" color="#bf0000" />
</div>
<div>
<div style="text-align:center" align="center">${event.title}</div>
<div style="background-image:url(/static/mobile/img/bg_bar.gif);background-color:#bf0000" bgcolor="#bf0000" background="/static/mobile/img/bg_bar.gif"><font color="#ffffff" size="3"><font color="#ffbf00">■</font>公演一覧</font></div>

%if len(performances) <= 0:
  現在表示できる公演はありません。
%else:
  %for p in performances:
	&#xe67d;${p.title}<br />
	　公演日:
	　${h.base.jdate(p.start_on)}
	  <br />
	　会場: ${p.venue}<br/>
    %if today > p.end_on:
    販売終了<br />
    %else:      
  	→<a href="${h.mobilelink.get_purchase_page_from_performance(request, p)}" target="_blank">購入ページへ</a><br />
    %endif
  %endfor
%endif

<div style="background-image:url(/static/mobile/img/bg_bar.gif);background-color:#bf0000" bgcolor="#bf0000" background="/static/mobile/img/bg_bar.gif"><font color="#ffffff" size="3"><font color="#ffbf00">■</font>公演詳細</font></div>
【公演期間】<br />
${h.base.jdate(event.event_open)}~${h.base.jdate(event.event_close)}<br />
%if event.performers:
【出演者】<br />
${event.performers}
%endif
%if event.notice:
【説明／注意事項】<br />
${h.base.nl_to_br(event.notice)}<br />
%endif
%if event.inquiry_for:
【お問い合わせ先】<br />
${event.inquiry_for}】<br />
%endif
【販売期間】<br />
[icon]${h.base.jterm(event.deal_open,event.deal_close)}<br />

</div>
<hr size="1" color="#888888" noshade="noshade" />
<div align="center">
  <div>
    <a href="http://ticket.rakuten.co.jp/static/faq/faq.html">ヘルプ</a> | <a href="http://www.ticketstar.jp/corporate">運営会社</a> | <a href="../mobile/contact/form">お問い合わせ</a> | <a href="http://www.ticketstar.jp/privacy">個人情報保護方針</a> | <a href="http://www.ticketstar.jp/legal">特定商取引法に基づく表示</a>
  </div>
<div><font color="#888888">2010-2011 &copy; TicketStar, Inc. All rights reserved.</font></div>
</div>
</font>
</body></html>
