<%inherit file='../layout_2col.mako'/>
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

<h3>アセット追加 / 編集</h3>

<div id="asset-form">
    ${form}
</div>
