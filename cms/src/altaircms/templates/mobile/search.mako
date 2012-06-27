<%namespace file="./components.mako" name="co"/>
<%inherit file="./outer.mako"/>
##
<div align="center">
${breadcrumbs} 『${freeword}』を含む公演
</div>

## breadcrumbs
    <div align="left" style="background-image: url(&quot;/static/mobile/img/bg_bar.gif&quot;); background-color: rgb(191, 0, 0);" bgcolor="#bf0000" background="/static/mobile/img/bg_bar.gif"><font color="#ffffff" size="3"><font color="#ffbf00">■</font>検索結果</font>
</div></div>

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
	  <a href="${h.mobilelink.publish_page_from_pageset(request,pageset)}">${pageset.name}</a><br>
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


