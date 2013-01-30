<%inherit file='../../layout_2col.mako'/>

<%namespace name="fco" file="../../formcomponents.mako"/>
<%namespace name="nco" file="../../navcomponents.mako"/>

<h2>layout 新規作成確認画面</h2>

<div class="row-fluid">
  <div class="span10">
    ${nco.breadcrumbs(
        names=["Top", "layout", u"新規作成", u"確認画面"], 
        urls=[request.route_path("dashboard"),
	          request.route_path("layout_list"),
              request.route_path("layout_create", action="input"),
	])
    }
  </div>
</div>

<%def name="form_to_table(form, x)">
<table class="table table-striped">
  <tbody>
  % for k in display_fields:
    <tr>
	  <td>${getattr(form,k).label}</td>
	  <td>${getattr(x,k)}</td>
	</tr>
  % endfor
  </tbody>
</table>
</%def>

<div class="row-fluid">
    <h3>layout追加 確認画面</h3>

	<div class="alert alert-info">
	  以下の内容のlayoutを作成します。良いですか？
	</div>

	##${form_to_table(form, master_env.mapper(request, obj))}

    <form action="${request.current_route_path(action="create")}" method="POST"
     enctype="multipart/form-data">
       ${fco.postdata_as_hidden_input(request.POST)}
        <button class="btn" type="submit">保存</button>
    </form>
</div>
