<%def name="page_difference(page,params)">
    <table class="table table-striped">
      <tr><th></th><th>変更前</th><th>変更後</th></tr>
      <tr>
        <th class="span2">ページ名</th><td class="span8">${page.title}</td><td class="span8">${params["title"]}</td>
      </tr>
      <tr>
        <th class="span2">所属イベント</th><td>${page.event.title if page.event else ""}</td><td class="span8">${params["event"]}</td>
      </tr>
      <tr>
        <th class="span2">親ページ</th><td>${page.title}</td><td class="span8">${params["parent"]}</td>
      </tr>
      <tr>
        <th class="span2">description</th><td>${page.description}</td><td  class="span8">${params["description"]}</td>
      </tr>
      <tr>
        <th class="span2">keywords</th><td>${page.keywords}</td><td class="span8">${params["keywords"]}</td>
      </tr>
      <tr>
        <th class="span2">url</th><td>${page.url}</td><td class="span8">${params["url"]}</td>
      </tr>
      <tr>
        <th class="span2">layout</th><td>${page.layout.title}</td><td class="span8">${params["layout"]}</td>
      </tr>
##      <tr>
##        <th class="span2">structure</th><td>${page.structure}</td><td class="span8">${params["structure"]}</td>
##      </tr>
    </table>
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
		  %for p in reversed(page.ancestors):
			<a class="parent" href="${h.page.to_edit_page(request,p)}">${p.title}</a> &raquo;
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
      <div id="detail"  class="widget blue float-left">イベント詳細</div>
      <div id="ticketlist"  class="widget red float-left">チケットリスト</div>
      <div id="performancelist"  class="widget red float-left">講演リスト</div>
      <div id="menu"  class="widget red float-left">メニュー</div>
      <div id="summary"  class="widget red float-left">サマリー</div>
      <div id="topic"  class="widget red float-left">トピック</div>
      <div id="breadcrumbs"  class="widget red float-left">パンくずリスト</div>
      <div id="countdown"  class="widget red float-left">カウントダウン</div>
      <div id="reuse"  class="widget red float-left">reuse</div>
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
<script type="text/javascript" src="/plugins/static/js/widget/lib/detail.js"></script>
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
<script type="text/javascript" src="/plugins/static/js/widget/lib/reuse.js"></script>
</%def>
