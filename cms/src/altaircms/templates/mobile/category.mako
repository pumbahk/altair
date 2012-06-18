<font size="1">
  <div align="center">
      <font color="red">
        
      </font>
  <a href="${request.route_path("mobile_index")}"><font color="#bf0000" size="3"><img src="/static/mobile/img/logo-small.gif" alt="楽天チケット" width="160" height="26"></font></a>
  <hr color="#bf0000" size="1" noshade="noshade">
  </div>
<div>
<div style="background-image: url(&quot;/static/mobile/img/bg_bar.gif&quot;); background-color: rgb(191, 0, 0);" bgcolor="#bf0000" background="images/bg_bar.gif"><font color="#ffffff" size="3"><font color="#ffbf00">■</font>${synonym}</font></div>
<div align="center">
  ${" / ".join(u'<a href="#">%s</a>' % c.label for c in subcategories)|n}
</div>

%if picks.count() > 0:
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
  
<div>
  <div style="background-image: url(&quot;/static/mobile/img/bg_bar.gif&quot;); background-color: rgb(191, 0, 0);" bgcolor="#bf0000" background="/static/mobile/img/bg_bar.gif"><font color="#ffffff" size="3"><font color="#ffbf00">■</font>今週発売のチケット</font></div>
      <a href="d/SPMSF">宮本文昭×新日本フィル〜真夏のチャイコフスキー〜</a>
  </div>

<div style="background-image: url(&quot;/static/mobile/img/bg_bar.gif&quot;); background-color: rgb(191, 0, 0);" bgcolor="#bf0000" background="/static/mobile/img/bg_bar.gif"><font color="#ffffff" size="3"><font color="#ffbf00">■</font>トピックス</font></div>
  <img src="/static/mobile/img/new.gif" width="23" height="8">
      <a href="../static/features/tube/index.html?top">TUBE野外ライブを楽チケで購入すると、メンバーサイン入りタオルをプレゼント！</a>
      <br>
</div>
<hr color="#bf0000" size="1" noshade="noshade">
<div style="background-color: rgb(255, 255, 187);" bgcolor="#ffffbb" align="center">
  <form action="http://ticket.rakuten.co.jp/mobile/s" class="searchbox"><font size="3">
    チケット検索<br>
    <input name="cid" value="2" type="hidden">
    <input class="text_field" name="q" value="" type="text"><input value="検索" type="submit">
  </font>
</form></div>


 
<hr color="#888888" size="1" noshade="noshade">
<div align="center">
  <div>
    <a href="http://ticket.rakuten.co.jp/static/faq/faq.html">ヘルプ</a> | <a href="http://www.ticketstar.jp/corporate">運営会社</a> | <a href="contact/form">お問い合わせ</a> | <a href="http://www.ticketstar.jp/privacy">個人情報保護方針</a> | <a href="http://www.ticketstar.jp/legal">特定商取引法に基づく表示</a>
  </div>
<div><font color="#888888">2010-2011 © TicketStar, Inc. All rights reserved.</font></div>
</div>
</font>
