<%inherit file='../layout.mako'/>
<%block name='js'>
    <script type="text/javascript" src="/static/deform/js/jquery.form.js"></script>
    <script type="text/javascript" src="/static/deform/js/jquery.maskedinput-1.2.2.min.js"></script>
    <script type="text/javascript" src="/static/deform/js/deform.js"></script>
</%block>
<%block name='style'>
    <link rel="stylesheet" href="/static/deform/css/form.css" type="text/css" />
</%block>
<%block name='jquery'>deform.load();</%block>

<h1>ウィジェット追加 / 編集</h1>

<a href="${request.route_url('widget_list')}">ウィジェット一覧</a>
<div id="widget-form">
    ${form}
</div>
