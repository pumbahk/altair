<%inherit file='../layout_2col.mako'/>
<%namespace name="nco" file="../navcomponents.mako"/>
<%namespace name="fco" file="../formcomponents.mako"/>
<%namespace name="mco" file="../modelcomponents.mako"/>
<%namespace name="gadgets" file="../gadgets.mako"/>

<div class="row-fluid">
    ${nco.breadcrumbs(
        names=["Top", "Event", event.title],
        urls=[request.route_path("dashboard"), request.route_path("event_list")]
    )}


<h2>${event.title}</h2>

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

  <div class="btn-group">
    <a href="${request.route_path("event_update",action="input",id=event.id)}" class="btn">
      <i class="icon-pencil"></i> 編集
    </a>
    <button class="btn dropdown-toggle" data-toggle="dropdown">
        <span class="caret"></span>
    </button>
    <ul class="dropdown-menu">
      <li>
        <a href="${request.route_path("event_update",action="input",id=event.id)}">
          <i class="icon-minus"></i> 編集
        </a>
      </li>
      <li>
        <a href="${request.route_path("event_create",action="input")}">
          <i class="icon-minus"></i> 新規作成
        </a>
      </li>
      <li>
        <a href="${request.route_path("event_delete",action="confirm",id=event.id)}">
          <i class="icon-minus"></i> 削除
        </a>
      </li>
    </ul>
  </div>

<hr/>

<h3>配下のページ一覧</h3>
<div class="box">
<table class="table">
  <thead>
	<tr>
	  <th></th><th>ページセット</th><th>ページ</th><th>現在表示状況</th><th>公開開始</th><th>公開終了</th><th>作成日時</th>
	</tr>
  </thead>
  <tbody>
    %for pageset in event.pagesets:
<%
pages = pageset.pages 
pagesize = len(pages)
current_page = pageset.current(published=True)
%>
    <tr>
      <td rowspan="${pagesize}">
        <input type="radio" name="object_id" value="${pageset.id}">
      </td>
      <td rowspan="${pagesize}">
        <a href="${request.route_path('pageset', pageset_id=pageset.id)}">${pageset.name}</a>
		<a class="action" target="_blank" href="${request.route_path("preview_pageset", pageset_id=pageset.id)}">
		  <i class="icon-eye-open"> </i></a>
       </a>
      </td>

	  %if len(pages) < 1:
	</tr>
	  %else:
      <td>
        <a href="${request.route_path('page_edit', event_id=event.id, page_id=pages[0].id)}">${pages[0].name}</a>
		<a class="action" target="_blank" href="${request.route_path("preview_page", page_id=pages[0].id)}">
		  <i class="icon-eye-open"> </i></a>
		${u'<span class="label">現在表示</span>' if pages[0]==current_page else u""|n}
      </td>
      <td>
			<div class="btn-group">
			  <a class="btn dropdown-toggle" data-toggle="dropdown" href="#">
				${u"公開中" if pages[0].published else u"非公開"}
				<span class="caret"></span>
			  </a>
			  <ul class="dropdown-menu">
				<!-- dropdown menu links -->
				<li><a href="${request.route_path("api_page_publish_status", status="publish", page_id=pages[0].id)}" class="publish_status">公開する</a></li>
				<li><a href="${request.route_path("api_page_publish_status", status="unpublish", page_id=pages[0].id)}" class="publish_status">非公開にする</a></li>
			  </ul>
			</div>
		</td>

	  <td>${pages[0].publish_begin}</td>
	  <td>${pages[0].publish_end}</td>
      <td>${pages[0].created_at}</td>
    </tr>
      %for page in pageset.pages[1:]:
      <tr>
		<td>
          <a href="${request.route_path('page_edit', event_id=event.id, page_id=page.id)}">${page.name}</a>
		  <a class="action" target="_blank" href="${request.route_path("preview_page", page_id=page.id)}">
			<i class="icon-eye-open"> </i></a>
		  ${u'<span class="label">現在表示</span>' if page==current_page else u""|n}
		</td>
		<td>
			<div class="btn-group">
			  <a class="btn dropdown-toggle" data-toggle="dropdown" href="#">
				${u"公開中" if page.published else u"非公開"}
				<span class="caret"></span>
			  </a>
			  <ul class="dropdown-menu">
				<!-- dropdown menu links -->
				<li><a href="${request.route_path("api_page_publish_status", status="publish", page_id=page.id)}" class="publish_status">公開する</a></li>
				<li><a href="${request.route_path("api_page_publish_status", status="unpublish", page_id=page.id)}" class="publish_status">非公開にする</a></li>
			  </ul>
			</div>
		</td>
		<td>${page.publish_begin}</td>
		<td>${page.publish_end}</td>
		<td>${page.created_at}</td>
	  </tr>
     %endfor
	 %endif
   %endfor
  </tbody>
</table>
  <div style="float:left;">

  </div>
  <div class="btn-group">
    <a class="btn action" target="_blank" href="${request.route_path("pageset", pageset_id="__id__")}">
      <i class="icon-plus"> </i> ページセット期間変更</a>
    </a>
    <button class="btn dropdown-toggle" data-toggle="dropdown">
      <span class="caret"></span>
    </button>
    <ul class="dropdown-menu">
	  <li>
		<a class="action" target="_blank" href="${request.route_path("pageset", pageset_id="__id__")}">
		  <i class="icon-plus"> </i> ページセット期間変更</a>
       </a>
	  </li>
     <li>
		<a class="" target="_blank" href="${request.route_path("page_add", event_id=event.id)}">
		  <i class="icon-plus"> </i> 新しいページセットの追加</a>
		</a>
     </li>
     <li>
	   <a id="pageset_addpage" class="individual-action" href="${request.route_path("pageset_addpage", pageset_id='__id__')}">
		 <i class="icon-plus"> </i> 選択したページセットにページ追加</a>
		</a>
<script type="text/javascript">
  $(function(){
  // swap status
  $(".box .publish_status").click(function(e){
    e.preventDefault();
    if(window.confirm("ステータスを「"+$(this).text()+"」に変更しますがよろしいですか？")){
      $.post($(this).attr("href")).done(function(){location.reload();});
    }
  });

  // add page
    $(".box #pageset_addpage").click(function(e){
      e.preventDefault();
      var  pk = $(this).parents(".box").find("input[name='object_id']:checked").val();
      if(!pk){ console.log("sorry"); return false; }
      $.post(String($(this).attr("href")).replace("__id__", pk)).done(function(){location.reload()}); //slackoff
      return false;
    });
  });
</script>
     </li>
<%doc>
      <li>
        <a href="${request.route_path("event_delete",action="confirm",id=event.id)}">
          <i class="icon-minus"></i> 削除
        </a>
      </li>
</%doc>
    </ul>
  </div>
</div>

<hr/>

<h3>パフォーマンス</h3>
<div class="box">
  <p align="right">※ pc購入URL,mobile購入URLは、個別に飛び先のURLが設定されている場合にy。そうでない場合にはnが付きます。</p>
  <table class="table">
    <thead><tr><th></th><th>公演名</th><th>バックエンドID</th><th>公演日時</th><th>場所</th><th>pc購入URL</th><th>mobile購入URL</th></tr>
    </thead>
    <tbody>
         %for p in performances:
           <tr>
             <td>
               <input type="radio" name="object_id" value="${p.id}">
             </td>
             <td><a href="${request.route_path("performance_update",action="detail",id=p.id)}">${p.title }</a></td>
             <td>${p.backend_id}</td><td>${ p.start_on }</td><td>${ p.venue }</td>
             <td>${u'<a href="%s">y</a>' % p.purchase_link if p.purchase_link else "n"|n}</td>
             <td>${u'<a href="%s">y</a>' % p.mobile_purchase_link if p.mobile_purchase_link else "n"|n}</td>
           </tr>
         %endfor
    </tbody>
  </table>

  ${gadgets.getti_update_code(performances,"getti_submit")}

  ## button group
  <div class="btn-group">
    <a href="${request.route_path("performance_update",action="input",id="__id__")}" class="btn action">
      <i class="icon-pencil"></i> 編集
    </a>
    <button class="btn dropdown-toggle" data-toggle="dropdown">
        <span class="caret"></span>
    </button>
    <ul class="dropdown-menu">
      <li>
        <a href="${request.route_path("performance_update",action="detail",id="__id__")}" class="action">
          <i class="icon-pencil"></i> 詳細画面
        </a>
      </li>
      <li>
        <a href="${request.route_path("performance_update",action="input",id="__id__")}" class="action">
          <i class="icon-minus"></i> 編集
        </a>
      </li>
      <li>
        <a href="${request.route_path("performance_create",action="input")}">
          <i class="icon-minus"></i> 新規作成
        </a>
      </li>
      <li>
        <a href="${request.route_path("performance_delete",action="confirm",id="__id__")}" class="action">
          <i class="icon-minus"></i> 削除
        </a>
      </li>
      <li class="divider"></li>
      <li>${ gadgets.getti_update_code_button()}</li>
    </ul>
  </div>
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

<script type="text/javascript">
  $(function(){
   $(".box .btn-group a.action").click(function(){
      var  pk = $(this).parents(".box").find("input[name='object_id']:checked").val();
      if(!pk){ console.log("sorry"); return false; }

      // initialize
      var $this = $(this);
      if (!$this.data("href-fmt")){
        $this.data("href-fmt", this.href);
      }
      this.href = $this.data("href-fmt").replace("__id__", pk);
      return true;;
    });
  })
</script>

</div>
