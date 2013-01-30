<div class="box">
  <table class="table">
    <thead>
      <tr>
		<th></th>
		<th>ページセット</th>
		<th>ページ</th>
		<th>表示状況</th>
		<th>公開開始</th>
		<th>公開終了</th>
		<th>作成日時</th>
      </tr>
    </thead>
    <tbody>
      %for pageset in pagesets:
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
          <a href="${h.link.pageset_detail(request,pageset)}">${pageset.name}</a>
          <a class="action" target="_blank" href="${request.route_path("preview_pageset", pageset_id=pageset.id)}">
            <i class="icon-eye-open"> </i></a>
         </a>
        </td>

        %if len(pages) < 1:
      </tr>
        %else:
        <td>
          <a href="${request.route_path('page_detail', page_id=pages[0].id)}">${pages[0].name}</a>
          <a class="action" target="_blank" href="${request.route_path("preview_page", page_id=pages[0].id)}">
            <i class="icon-eye-open"> </i></a>
          <a class="action" target="_blank" href="${request.route_path("page_edit_", page_id=pages[0].id)}">
            <i class="icon-edit"> </i></a>
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
                  <li><a href="${request.route_path("plugins_jsapi_page_publish_status", status="publish", page_id=pages[0].id)}" class="publish_status">公開する</a></li>
                  <li><a href="${request.route_path("plugins_jsapi_page_publish_status", status="unpublish", page_id=pages[0].id)}" class="publish_status">非公開にする</a></li>
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
            <a href="${request.route_path('page_detail', page_id=page.id)}">${page.name}</a>
            <a class="action" target="_blank" href="${request.route_path("preview_page", page_id=page.id)}">
              <i class="icon-eye-open"> </i></a>
            <a class="action" target="_blank" href="${request.route_path("page_edit_", page_id=page.id)}">
              <i class="icon-edit"> </i></a>

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
                  <li><a href="${request.route_path("plugins_jsapi_page_publish_status", status="publish", page_id=page.id)}" class="publish_status">公開する</a></li>
                  <li><a href="${request.route_path("plugins_jsapi_page_publish_status", status="unpublish", page_id=page.id)}" class="publish_status">非公開にする</a></li>
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
  <div class="btn-group">
    <a class="btn action" target="_blank" href="${request.route_path("pageset", pageset_id="__id__")}">
      <i class="icon-plus"> </i> ページセット期間変更</a>
    <button class="btn dropdown-toggle" data-toggle="dropdown">
      <span class="caret"></span>
    </button>
    <ul class="dropdown-menu">
	  <li>
		<a class="action" target="_blank" href="${request.route_path("pageset", pageset_id="__id__")}">
		  <i class="icon-plus"> </i> ページセット期間変更</a>
	  </li>
	  <li>
		<a href="${request.route_path("event_takein_pageset",event_id=event.id)}">
		  <i class="icon-plus">_</i> このイベントに配下のページとして別のページセットを取り込む</a>
	  </li>
	  <li>
		<a id="reset_event" class="individual-action" href="${request.route_path("plugins_jsapi_pageset_reset_event", pageset_id="__id__")}">
		  <i class="icon-plus"> </i> 選択したページセットをイベントと結びつかないページセットにする</a>
	  </li>
     <li>
		<a class="" href="${request.route_path("page_add", event_id=event.id, action="input")}">
		  <i class="icon-plus"> </i> 新しいページセットの追加</a>
     </li>
     <li>
	   <a id="pageset_addpage" class="individual-action" href="${request.route_path("plugins_jsapi_addpage", pageset_id='__id__')}">
		 <i class="icon-plus"> </i> 選択したページセットにページ追加</a>

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
  // reset event
    $(".box #reset_event").click(function(e){
      e.preventDefault();
      var  pk = $(this).parents(".box").find("input[name='object_id']:checked").val();
      if(!pk){ console.log("sorry"); return false; }
      $.post(String($(this).attr("href")).replace("__id__", pk)).done(function(){location.reload()}); //slackoff
      return false;
    });
  });
</script>
     </li>
    </ul>
  </div>
</div>
