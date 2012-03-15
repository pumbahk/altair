<%def name="page_difference(page,params)">
    <table class="table table-striped">
      <tr><th></th><th>変更前</th><th>変更後</th></tr>
      <tr>
        <th class="span2">ページ名</th><td class="span8">${page.title}</td><td>${params["title"]}</td>
      </tr>
      <tr>
        <th class="span2">description</th><td>${page.description}</td><td>${params["description"]}</td>
      </tr>
      <tr>
        <th class="span2">keywords</th><td>${page.keywords}</td><td>${params["keywords"]}</td>
      </tr>
      <tr>
        <th class="span2">url</th><td>${page.url}</td><td>${params["url"]}</td>
      </tr>
      <tr>
        <th class="span2">layout</th><td>${page.layout.title}</td><td>${params["layout"]}</td>
      </tr>
##      <tr>
##        <th class="span2">structure</th><td>${page.structure}</td><td>${params["structure"]}</td>
##      </tr>
    </table>
</%def>
<%def name="page_description(page)">
    <table class="table table-striped">
      <tr>
        <th class="span2">ページ名</th><td class="span8">${page.title}</td>
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
      <div id="topic"  class="widget red float-left">トピック</div>
      <div id="topic"  class="widget red float-left">パンくずリスト</div>
    </div>
</%def>

<%def name="render_blocks(blocks)">
  <div id="wrapped">
    % for name  in blocks:
      <div id="${name}" class="block noitem">${name}</div>
    % endfor
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
</%def>
