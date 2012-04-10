<%inherit file='../layout_2col.mako'/>
<%namespace name="nco" file="../navcomponents.mako"/>
<%namespace name="fco" file="../formcomponents.mako"/>

<h2>layout</h2>

<div class="row-fluid">
  <div class="span10">
    ${nco.breadcrumbs(
	    names=["Top", "Layout"], 
	    urls=[request.route_path("dashboard")]
	)}
  </div>
</div>

<div class="row">
    <div class="span6">
        <h4>レイアウト</h4>
        <form action="#" method="POST">
        ${fco.form_as_table_strict(form, ["title", "blocks", "template_filename"])}
            <button class="btn" type="submit">保存</button>
        </form>
    </div>
</div>

<hr/>

<div class="row">
    <ul class="nav nav-list">
        <li class="nav-header">登録済みレイアウト</li>
        %for layout in layouts['layouts']:
                <li><a href="${request.route_path('layout', layout_id=layout['id'])}">${layout['title']}</a></li>
        %endfor
    </ul>
</div>
