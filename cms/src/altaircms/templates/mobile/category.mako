<%namespace file="./components.mako" name="co"/>
<%inherit file="./footer.mako"/>

<head>
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
  <title>チケット販売・イベントの予約 [音楽 / コンサート / 舞台 / スポーツ] - 楽天チケット</title>
</head>
<body bgcolor="#ffffff"><font size="1">
  <div align="center">
      <font color="red">
      </font>
  <a href="${request.route_path("mobile_index")}"><font color="#bf0000" size="3"><img src="/static/mobile/img/logo-small.gif" alt="楽天チケット" width="160" height="26"></font></a>
  <hr color="#bf0000" size="2" noshade="noshade">
  </div>
<div>
<a href="${request.route_path("mobile_index")}">トップ</a>
<div style="background-image: url(&quot;/static/mobile/img/bg_bar.gif&quot;); background-color: rgb(191, 0, 0);" bgcolor="#bf0000" background="images/bg_bar.gif"><font color="#ffffff" size="3"><font color="#ffbf00">■</font>${synonym}</font></div>
<div align="center">
  ${" / ".join(u'<a href="%s">%s</a>' % (request.route_path("mobile_search",_query=dict(q=c.label, r=root.name)),c.label) for c in subcategories)|n}
</div>

%if picks.count() > 0:
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
  
<div>

%if events_on_sale.count() > 0:
  <div style="background-image: url(&quot;/static/mobile/img/bg_bar.gif&quot;); background-color: rgb(191, 0, 0);" bgcolor="#bf0000" background="/static/mobile/img/bg_bar.gif"><font color="#ffffff" size="3"><font color="#ffbf00">■</font>今週発売のチケット</font></div>
  %for pageset in events_on_sale:
	 <a href="${request.route_path("mobile_detail",pageset_id=pageset.id)}">${pageset.name}</a>
  %endfor
  </div>
%endif

%if topics.count() > 0:
<div style="background-image: url(&quot;/static/mobile/img/bg_bar.gif&quot;); background-color: rgb(191, 0, 0);" bgcolor="#bf0000" background="/static/mobile/img/bg_bar.gif"><font color="#ffffff" size="3"><font color="#ffbf00">■</font>トピックス</font></div>
  %for topic in topics:
	<img src="/static/mobile/img/new.gif" width="23" height="8">
		<a href="${h.mobilelink.get_link_from_topic(request,topic)}">${topic.title}</a>
		<br>
  %endfor
%endif
</div>

<hr color="#bf0000" size="1" noshade="noshade">
<div style="background-color: rgb(255, 255, 187);" bgcolor="#ffffbb" align="center">
   ${co.search_form(request)}
</div>

