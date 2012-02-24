<%inherit file='../layout_2col.mako'/>
<%block name='js'>
    <script type="text/javascript" src="/static/js/jquery.form.js"></script>
    <script type="text/javascript" src="/static/js/jquery.maskedinput.js"></script>
    <script type="text/javascript" src="/static/deform/js/deform.js"></script>
</%block>
<%block name='style'>
    <link rel="stylesheet" href="/static/deform/css/form.css" type="text/css" />
</%block>
<%block name="jquery">
deform.load();
</%block>

<h1>レイアウト</h1>

<div id="layout-form">${form}</div>

<hr/>

<ul>
%for layout in layouts:
<li><a href="${request.route_url('layout', layout_id=layout.id)}">${layout}</a></li>
%endfor
</ul>
