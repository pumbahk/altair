<%namespace name="fco" file="../formcomponents.mako"/>

<%def name="setup_info_form()">
	<script type="text/javascript">
	  var propagate_data = function(data){
		var root = $("form#submit_form");
		root.find("input[name='name']").val(data.name);
		root.find("textarea[name='url']").val(data.url);
		root.find("textarea[name='title']").val(data.title);
		root.find("textarea[name='keywords']").val(data.keywords);
		root.find("textarea[name='description']").val(data.description);

	    //$('label[for="url"]').text(data.jurl);

		var parent_field = root.find("select[name='parent']");
		if(data.parent){
	      parent_field.val(data.parent).removeAttr("disabled");
		} else {
	      parent_field.attr("disabled","disabled");
	    }
	  }
	  
	  var propagete_setup_info = function(){
	    var root = $("form#setup_form");
	    var params = {"name": root.find("input[name='name']").val(),
	                  "parent": root.find("select[name='parent']").val()};
		$.getJSON("${request.route_path("plugins_api_page_info_default")}",params).done(function(data,status,req){
		  if (data.error){
			alert(data.error);
		  } else {
	        propagate_data(data);
	  	    console.log(data);
		  }
		}).fail(function(data){console.log(data)})
	    return false; // kill propagation
	  };
	</script>
	<form id="setup_form" onSubmit="return propagete_setup_info();">
     ${fco.form_as_table_strict(setup_form, ["parent", "name"])}
	 <input type="submit" value="初期値をフォームに反映">
	</form>
</%def>

<%def name="page_difference(page,params)">
    <table class="table table-striped">
      <tr><th></th><th>変更前</th><th>変更後</th></tr>
	  <%
parent = page.pageset.parent
event = page.event or page.pageset.event
%>
      <tr><th class="span2">親ページ</th><td>${parent.name if parent else u"-"}</td><td>${(parent.name if parent else u"-") if params["parent"] == "__None" else params["parent"] }</td></tr>
      <tr><th class="span2">所属イベント</th><td>${event.title if event else ""}</td><td>${(event.title if event else "") if params["event"] == "__None" else params["event"]}</td></tr>
      <tr><th class="span2">ページ名</th><td>${page.name}</td><td>${params["name"]}</td></tr>
      <tr><th class="span2">URL</th><td>${page.url}</td><td>${params["url"]}</td></tr>
      <tr><th class="span2">タイトル</th><td>${page.title}</td><td>${params["title"]}</td></tr>
      <tr><th class="span2">公開開始日</th><td>${page.publish_begin}</td><td>${params["publish_begin"]}</td></tr>
      <tr><th class="span2">公開終了日</th><td>${page.publish_end}</td><td>${params["publish_end"]}</td></tr>
      <tr><th class="span2">description</th><td>${page.description}</td><td>${params["description"]}</td></tr>
      <tr><th class="span2">keywords</th><td>${page.keywords}</td><td>${params["keywords"]}</td></tr>
      <tr><th class="span2">公開タグ</th><td>${u",".join([t.label for t in page.tags])}</td><td>${params["tags"]}</td></tr>
      <tr><th class="span2">非公開タグ</th><td>${u",".join([t.label for t in page.private_tags])}</td><td>${params["private_tags"]}</td></tr>
      <tr><th class="span2">レイアウト</th><td>${page.layout.title}</td><td>${params["layout"]}</td></tr>
</%def>

<%def name="page_description(page)">
    <table class="table table-striped">
      <tr>
        <th class="span2">ページ名</th><td class="span8">${page.title}</td>
      </tr>
      <tr>
        <th class="span2">関連イベント</th><td class="span8"><a href="${h.page.event_page(request,page)}">${page.event.title if page.event else ""}</a></td>
      </tr>
      <tr>
        <th class="span2">description</th><td>${page.description}</td>
      </tr>
      <tr>
        <th class="span2">keywords</th><td>${page.keywords}</td>
      </tr>
      <tr>
        <th class="span2">url</th><td>${page.url}</td>
      </tr>
      <tr>
        <th class="span2">layout</th><td>${page.layout.title}</td>
      </tr>
##      <tr>
##        <th class="span2">structure</th><td>${page.structure}</td>
##      </tr>
      <tr>
	<th>掲載期間</th>
	<td>開始: ${page.publish_begin} <br /> 終了: ${page.publish_end}</td>
      </tr>
      <tr>
        <th class="span2">公開ステータス</th><td>${h.page.show_publish_status(page)}</td>
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
        <th class="span2">公開タグ</th>
		<td>
		  %for tag in page.public_tags:
			<a class="tag" href="${h.tag.to_search_query(request, "page", tag)}">${tag.label}</a> ,
          %endfor
        </td>
      </tr>
      <tr>
        <th class="span2">非公開タグ</th>
		<td>
		  %for tag in page.private_tags:
			<a class="tag" href="${h.tag.to_search_query(request, "page", tag)}">${tag.label}</a> ,
          %endfor
        </td>
      </tr>
    </table>
</%def>

<%def name="widget_palets()">
    <div id="widget_palet">
      <div id="image" class="widget red float-left">画像</div>
      <div id="freetext" class="widget blue float-left">フリーテキスト</div>
      <div id="flash"  class="widget green float-left">flash</div>
      <div id="movie"  class="widget gray float-left">動画</div>
      <div id="calendar"  class="widget green float-left">カレンダー</div>
      <!-- <div id="detail"  class="widget blue float-left">イベント詳細</div> -->
      <div id="ticketlist"  class="widget red float-left">チケットリスト</div>
      <div id="performancelist"  class="widget red float-left">公演リスト</div>
      <div id="menu"  class="widget red float-left">メニュー</div>
      <div id="summary"  class="widget red float-left">サマリー</div>
      <div id="iconset"  class="widget red float-left">アイコンセット</div>
      <div id="topic"  class="widget red float-left">トピック</div>
      <div id="breadcrumbs"  class="widget red float-left">パンくずリスト</div>
      <div id="countdown"  class="widget red float-left">カウントダウン</div>
      <!-- <div id="reuse"  class="widget red float-left">reuse</div> -->
      <div id="linklist"  class="widget red float-left">リンクリスト</div>
      <div id="heading"  class="widget red float-left">見出し</div>
      <div id="promotion"  class="widget red float-left">プロモーション枠</div>
      <div id="anchorlist"  class="widget red float-left">ページ内リンク一覧</div>
      <div id="purchase"  class="widget red float-left">購入ボタン</div>
      <div id="twitter"  class="widget red float-left">twitter</div>
    </div>
</%def>

<%def name="render_blocks(blocks)">
  <div id="wrapped">
%for row in blocks.structure:
    %for name in row:
      <div class="block noitem size${len(row)} left" id="${name}">
        ${name}
      </div>
    %endfor
  %if len(row) > 1:
    <div class="clear"/>
  %endif
%endfor
##    % for name  in blocks:
##      <div id="${name}" class="block noitem">${name}</div>
##    % endfor
  </div>
</%def>

<%def name="widget_js_scripts()">
<script type="text/javascript" src="/static/js/my/widgets/base.js"></script>
## todo: moveit
<script type="text/javascript" src="/plugins/static/js/widget/lib/image.js"></script>
## todo: moveit
<script type="text/javascript" src="/plugins/static/js/widget/lib/freetext.js"></script>
## todo: moveit
<script type="text/javascript" src="/plugins/static/js/widget/lib/movie.js"></script>
## todo: moveit
<script type="text/javascript" src="/plugins/static/js/widget/lib/flash.js"></script>
## todo: moveit
<script type="text/javascript" src="/plugins/static/js/widget/lib/calendar.js"></script>
## todo: moveit
##<script type="text/javascript" src="/plugins/static/js/widget/lib/detail.js"></script>
## todo: moveit
<script type="text/javascript" src="/plugins/static/js/widget/lib/ticketlist.js"></script>
## todo: moveit
<script type="text/javascript" src="/plugins/static/js/widget/lib/performancelist.js"></script>
## todo: moveit
<script type="text/javascript" src="/plugins/static/js/widget/lib/menu.js"></script>
## todo: moveit
<script type="text/javascript" src="/plugins/static/js/widget/lib/topic.js"></script>
## todo: moveit
<script type="text/javascript" src="/plugins/static/js/widget/lib/breadcrumbs.js"></script>
## todo: moveit
<script type="text/javascript" src="/plugins/static/js/widget/lib/summary.js"></script>
## todo: moveit
<script type="text/javascript" src="/plugins/static/js/widget/lib/countdown.js"></script>
## todo: moveit
##<script type="text/javascript" src="/plugins/static/js/widget/lib/reuse.js"></script>
## todo: moveit
<script type="text/javascript" src="/plugins/static/js/widget/lib/iconset.js"></script>
## todo: moveit
<script type="text/javascript" src="/plugins/static/js/widget/lib/linklist.js"></script>
## todo: moveit
<script type="text/javascript" src="/plugins/static/js/widget/lib/heading.js"></script>
## todo: moveit
<script type="text/javascript" src="/plugins/static/js/widget/lib/promotion.js"></script>
## todo: moveit
<script type="text/javascript" src="/plugins/static/js/widget/lib/anchorlist.js"></script>
## todo: moveit
<script type="text/javascript" src="/plugins/static/js/widget/lib/purchase.js"></script>
## todo: moveit
<script type="text/javascript" src="/plugins/static/js/widget/lib/twitter.js"></script>
</%def>
