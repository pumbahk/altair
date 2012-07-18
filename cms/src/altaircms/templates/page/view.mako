<%inherit file='../layout_2col.mako'/>
<%namespace name="co" file="./components.mako"/>
<%namespace name="nco" file="../navcomponents.mako"/>
<%namespace name="fco" file="../formcomponents.mako"/>
<%namespace name="mco" file="../modelcomponents.mako"/>
<%namespace name="gadgets" file="../gadgets.mako"/>

<%block name="style">
<style type="text/css">
#appendix h3{ 
  margin-top:20px;
}
</style>
</%block>

<div class="row-fluid">
%if page.event:
    ${nco.breadcrumbs(
        names=["Top", "Event", page.event.title, page.name],
        urls=[request.route_path("dashboard"),
              request.route_path("event_list"),
              request.route_path("event", id=page.event.id)
              ]
    )}
%else:
    ${nco.breadcrumbs(
        names=["Top", "Page", page.name],
        urls=[request.route_path("dashboard"),
              request.route_path("pageset_detail", pageset_id=page.pageset.id, kind=page.kind),
              ]
    )}
%endif

<h2>${page.name}</h2>
	  <%
parent = page.pageset.parent
event = page.event or page.pageset.event
%>
    <table class="table table-striped">
      <tr>
        <th class="span2">ページ名</th>
		<td>
		  ${page.title}
 		  <a target="_blank" href="${request.route_path("preview_page", page_id=page.id)}"><i class="icon-eye-open"> </i></a>
		</td>
      </tr>
      <tr>
        <th class="span2">所属イベント</th><td><a href="${h.page.event_page(request,page)}">${page.event.title if page.event else ""}</a></td>
      </tr>
      <tr>
        <th class="span2">親ページ</th>
		<td>
		  %for p in reversed(page.pageset.ancestors if page.pageset else []):
			<a class="parent" href="${request.route_path("pageset", pageset_id=p.id)}">${p.name}</a> &raquo;
          %endfor
        </td>
      </tr>
      <tr>
        <th class="span2">タイトル</th><td>${page.title}</td>
      </tr>
      <tr>
        <th class="span2">description</th><td>${page.description}</td>
      </tr>
      <tr>
        <th class="span2">キーワード</th><td>${page.keywords}</td>
      </tr>
      <tr>
        <th class="span2">レイアウト</th><td>${page.layout.title if page.layout else u""}</td>
      </tr>
      <tr>
		<th>掲載期間</th>
		<td>${h.base.jterm(page.publish_begin, page.publish_end)}</td>
      </tr>
      <tr>
        <th class="span2">公開ステータス</th><td>${u"公開中" if page.published else u"非公開"}</td>
      </tr>
    </table>

  <div class="btn-group" style="float:left; margin-bottom:20px; margin-right:10px;">
    <a target="_blank" href="${request.route_path("page_update",id=page.id)}" class="btn">
      <i class="icon-pencil"></i> ページ基本情報編集
    </a>
    <a class="btn dropdown-toggle" data-toggle="dropdown">
        <span class="caret"></span>
    </a>
    <ul class="dropdown-menu">
	  <li>
		<a target="_blank" href="${request.route_path("page_update",id=page.id)}" class="">
		  <i class="icon-pencil"></i> ページ基本情報編集
		</a>
	  </li>
      <li>
		<a target="_blank" href="${request.route_path("page_edit_", page_id=page.id)}"><i class="icon-minus"></i> ページのレイアウト編集</a>
      </li>
	  <li>
		<a href="${h.page.to_delete(request,page)}"><i class="icon-trash"></i> ページの削除</a>
	  </li>
	  <li class="divider"></li>
	  <li>
	   	<a target="_blank" href="${request.route_path("preview_page", page_id=page.id)}"><i class="icon-eye-open"></i>Preview</a>
	  </li>
    </ul>
  </div>

  <div>
  <a target="_blank" href="${request.route_path("page_edit_", page_id=page.id)}" class="btn">D&Dとwidgetでページレイアウト編集</a>

	%if page.published:
	<button 
	   href="${request.route_path("plugins_jsapi_page_publish_status", status="unpublish", page_id=page.id)}"
	   id="publish_status" class="btn btn-inverse"><i class="icon-plus icon-white"></i>ページを非公開</button>
	%else:
	<button 
	   href="${request.route_path("plugins_jsapi_page_publish_status", status="publish", page_id=page.id)}"
	   id="publish_status" class="btn btn-info"><i class="icon-plus"></i>ページを公開</button>
	%endif
  </div>

<script type="text/javascript">
  $(function(){
      // swap status
	$("#publish_status").click(function(e){
	  e.preventDefault();
	  if(window.confirm("「"+$(this).text()+"」しますがよろしいですか？\n\n(公開したページは、特別な権限を持たない限り変更できなくなります。)")){
		$.post($(this).attr("href")).done(function(){location.reload();});
	  }
	});
  });
</script>
  <div style="clear:both;"></div>

<div id="appendix">
   <h3>タグ</h3>
   ${myhelpers.pagetag_describe_viewlet(request, page)}
   <hr/>
   ##<h3>ホットワード</h3>
   ##${myhelpers.hotword_describe_viewlet(request, page)}
   <h3>アクセスキー</h3>
   ${myhelpers.accesskey_describe_viewlet(request, page)}
   <h3>アセット</h3>
   <h3>トピック</h3>
   <h3>トップコンテンツ</h3>
</div>

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


