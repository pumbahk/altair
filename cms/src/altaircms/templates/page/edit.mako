##
##
##
<%inherit file='../layout.mako'/>
<%namespace name="co" file="components.mako"/>
<%namespace name="css" file="internal.css.mako"/>

<%block name='js'>
    <script type="text/javascript" src="/static/deform/js/jquery.form.js"></script>
    <script type="text/javascript" src="/static/deform/js/deform.js"></script>
    <script type="text/javascript" src="/static/deform/js/jquery.maskedinput-1.2.2.min.js"></script>
</%block>
<%block name='style'>
    <link rel="stylesheet" href="/static/deform/css/form.css" type="text/css" />
    ${css.edit()}
</%block>
<%block name='js_foot'>
    <script type="text/javascript">
	  ${co.form()}
    </script>
</%block>

%if page and event:
<h1>イベント${event}の${page}の編集</h1>
%elif event:
<h1>イベント${event}のページ追加</h1>
%elif page:
<h1>${page}ページの編集</h1>
%endif

%if event:
<a href="${request.route_url('event', id=event.id)}">back</a>
%endif

<div id="pageform">
    ${form|n}
</div>


<div id="pagecontentform">
    <div id="pagelayout">レイアウト選択</div>
    <div id="pageversion">ページのバージョンが入る</div>
    <div id="pagewidget">ウィジェット</div>
    <br class="clear"/>
    <form action="#" method="post">
        <div id="page">ページ編集</div>
        <button type="submit">保存</button>
    </form>
</div>
