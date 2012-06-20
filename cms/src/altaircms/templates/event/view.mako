<%inherit file='../layout_2col.mako'/>
<%namespace name="nco" file="../navcomponents.mako"/>
<%namespace name="fco" file="../formcomponents.mako"/>
<%namespace name="mco" file="../modelcomponents.mako"/>
<%namespace name="gadgets" file="./gadgets.mako"/>

<div class="row-fluid">
    ${nco.breadcrumbs(
	    names=["Top", "Event", event.title],
	    urls=[request.route_path("dashboard"), request.route_path("event_list")]
	)}

<h2>${event.title} (ID: ${event.id})</h2>

<table class="table table-striped">
      <tr>
        <th class="span2">タイトル</th><td>${event.title}</td>
      </tr>
      <tr>
        <th class="span2">サブタイトル</th><td>${event.subtitle}</td>
      </tr>
      <tr>
        <th class="span2">バックエンド管理番号</th><td>${event.backend_id}</td>
      </tr>
      <tr>
        <th class="span2">概要</th><td>${event.description}</td>
      </tr>
      <tr>
        <th>開催期間</th><td>${h.base.jterm(event.event_open,event.event_close)}</td>
      </tr>
      <tr>
        <th>販売期間</th><td>${h.base.jterm(event.deal_open,event.deal_close)}</td>
      </tr>
      <tr>
        <th class="span2">出演者</th><td>${event.performers}</td>
      </tr>
      <tr>
        <th class="span2">説明/注意事項</th><td>${event.notice}</td>
      </tr>
      <tr>
        <th class="span2">問い合わせ先</th><td>${event.inquiry_for}</td>
      </tr>
    </table>

  <div class="btn-group" style="float: left;">
	<a class="btn" href="${request.route_path("page_add", event_id=event.id)}">
	  <i class="icon-plus"> </i> ページ追加</a>
	</a>
  <%doc>
	<button class="btn dropdown-toggle" data-toggle="dropdown">
	  <span class="caret"></span>
	</button>
	<ul class="dropdown-menu">
	  <li>
		<a href="${request.route_path("event_delete",action="confirm",id=event.id)}">
		  <i class="icon-minus"></i> 削除
		</a>
	  </li>
	</ul>
  </%doc>
  </div>

<div style="clear: left;"></div>
<hr/>


<h3>配下のページ一覧</h3>
<div class="box">
<table class="table">
  <tbody>
	%for pageset in event.pagesets:
	<tr>
	  <td>
		<a href="${request.route_path('pageset', pageset_id=pageset.id)}">${pageset.name}</a>
		<a class="btn btn-small" href="${h.link.to_preview_page_from_pageset(request,pageset)}" target="_blank"><i class="icon-eye-open"> </i> preview</a>
	  </td>
   </tr>
   %endfor
  </tbody>
</table>
</div>

<h3>パフォーマンス</h3>
<div class="box">
  <table class="table">
	<thead><tr><th></th><th>公演名</th><th>バックエンドID</th><th>公演日時</th><th>場所</th></tr>
	</thead>
	<tbody>
		 %for p in performances:
		   <tr>
			 <td>
			   <input type="radio" name="object_id" value="${p.id}">
			 </td>
			 <td>${p.title }</td>
			 <td>${p.backend_id}</td><td>${ p.start_on }</td><td>${ p.venue }</td>
		   </tr>
		 %endfor
	</tbody>
  </table>
  ${gadgets.multiple_action_button(request,"performance")}
</div>

<hr/>

<h3>販売条件情報</h3>
<div class="box">
<table class="table">
  <thead><tr><th></th><th>名前</th><th>販売条件</th><th>適用期間</th><th>券種</th><th>席種</th><th>価格</th></tr>
  </thead>
  <tbody>
	 %for sale in sales:
<%
tickets = sale.tickets
tickets_size = len(tickets)
 %>
	   <tr>
		 <td rowspan="${ tickets_size }">
		   <input type="radio" name="object_id" value="${sale.id}">
		 </td>
		 <td rowspan="${ tickets_size }">${ sale.name }</td>
		 <td rowspan="${ tickets_size }">${sale.jkind}</td>
         <td rowspan="${ tickets_size }">${ h.base.jterm(sale.start_on,sale.end_on) if sale.start_on and sale.end_on else u"~"}</td>
%if len(tickets) <= 0:
	   </tr>
%else:
	     <td><a href="${request.route_path("ticket_update",action="input",id=tickets[0].id)}">${tickets[0].name}</a></td>
		 <td>${tickets[0].seattype}</td>
		 <td>${tickets[0].price}</td>
	   </tr>
	   %for t in tickets[1:]:
		 <tr>
	     <td><a href="${request.route_path("ticket_update",action="input",id=t.id)}">${t.name}</a></td>
		 <td>${t.seattype}</td>
		 <td>${t.price}</td>
		 </tr>
	   %endfor
%endif
     %endfor
  </tbody>
</table>
${gadgets.multiple_action_button(request,"sale")}
</div>

<%doc>
<h3>チケット情報</h3>
<table class="table">
  <thead><tr><th>名前</th><th>販売条件</th><th>開始日</th><th>終了日</th></tr>
  </thead>
  <tbody>

	   %for sale in sales:
	     <tr><td>${sale.name}</td><td><a href="${request.route_path("sale_update",id=sale.id,action="input")}">　${sale.jkind}　</a></td><td>${ sale.start_on }</td><td>${ sale.end_on }</td></tr>


		 <tr>
		   <td colspan=3>
		   <ul>
		   % for t in sale.tickets:
		     <li><a href="${request.route_path("ticket_update",action="input",id=t.id)}">${t.name}(${t.seattype}): ${t.price}</a></li>
		   % endfor
		   </ul>
		   </td>
		 </tr>
	   %endfor		 
</%doc>

</div>
${gadgets.multiple_action_button_script()}
