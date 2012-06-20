<%inherit file='../layout_2col.mako'/>
<%namespace name="nco" file="../navcomponents.mako"/>
<%namespace name="fco" file="../formcomponents.mako"/>
<%namespace name="mco" file="../modelcomponents.mako"/>

<h2>${event.title} (ID: ${event.id})</h2>

<div class="row-fluid">
  <div class="span10">
    ${nco.breadcrumbs(
	    names=["Top", "Event", event.title],
	    urls=[request.route_path("dashboard"), request.route_path("event_list")]
	)}
  </div>
</div>


<div class="row-fluid">
  <div class="span5">
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
        <th>開催期間</th><td>${event.event_open} - ${event.event_close}</td>
      </tr>
      <tr>
        <th>販売期間</th><td>${event.deal_open} - ${event.deal_close}</td>
      </tr>
      <tr>
        <th class="span2">開催場所</th><td>${event.place}</td>
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
  </div>

  ## operation
  <div class="span6">
    <a class="btn" href="${request.route_path("page_add", event_id=event.id)}"><i class="icon-plus"> </i> ページ追加</a>
    <a href="${request.route_path("event_update",action="input",id=event.id)}" class="btn "><i class="icon-cog "> </i> Update</a>
    <a class="btn" href=""><i class="icon-refresh"> </i> Sync</a>
  </div>

<hr/>

  <div class="span5">

	<h3>配下のページ一覧</h3>
	  <table class="table">
		<tbody>
		  %for pageset in event.pagesets:
			<tr>
			  <td>
				<a href="${request.route_path('pageset', pageset_id=pageset.id)}">${pageset.name}</a>
				    <a class="btn btn-small" href="${h.link.to_preview_page_from_pageset(request,pageset)}" target="_blank"><i class="icon-eye-open"> </i> </a>
			  </td>
               </td>
			</tr>
		  %endfor
		</tbody>
	  </table>
  </div>
</div>

<div class="row">
  <div class="span5">
	<h3>パフォーマンス</h3>
   <table>
	 <thead><tr><th>公演名</th><th>公演日時</th><th>場所</th></tr>
	 </thead>
	 <tbody>
	   %for p in performances:
	     <tr><td><a href="${request.route_path("performance_update",id=p.id,action="input")}">${p.title}</a></td><td>${ p.start_on }</td><td>${ p.venue }</td></tr>
	   %endfor
	 </tbody>
   </table>
  </div>

  <div class="span5">
  <h3>チケット情報</h3>
   <table>
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
		 
	 </tbody>
   </table>
  </div>

</div>

