<%inherit file='../layout.mako'/>

<h1>レイアウト - ${layout}</h1>
<a href="${request.route_url("layout_list")}">back</a>

<hr/>

ID: ${layout.id}<br/>
名称: ${layout.title}<br/>
テンプレートファイル名: ${layout.template_filename}
