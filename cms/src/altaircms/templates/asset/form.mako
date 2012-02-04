<%inherit file='../layout.mako'/>
<%block name='js'>
    <script type="text/javascript" src="/static/js/jquery.form.js"></script>
    <script type="text/javascript" src="/static/js/jquery.maskedinput.js"></script>
    <script type="text/javascript" src="/static/deform/js/deform.js"></script>
</%block>
<%block name='style'>
    <link rel="stylesheet" href="/static/deform/css/form.css" type="text/css" />
</%block>
<%block name='jquery'>
    deform.load();
</%block>

<h1>アセット追加 / 編集</h1>

<a href="${request.route_url('asset_list')}">アセット一覧</a>
<div id="asset-form">
    ${form}
</div>
