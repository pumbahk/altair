<%inherit file='../../layout_2col.mako'/>

<%namespace name="fco" file="../../formcomponents.mako"/>
<%namespace name="nco" file="../../navcomponents.mako"/>

<h2>layout 新規作成</h2>

<div class="row-fluid">
  <div class="span10">
    ${nco.breadcrumbs(
        names=["Top", "layout", u"新規作成"], 
        urls=[request.route_path("dashboard"),
	          request.route_path(("layout_list"))])
    }
  </div>
</div>

<div class="row-fluid">
    <h3>layout追加</h3>
    <form action="${request.current_route_path(action="create")}" method="POST"
     enctype="multipart/form-data">
       ${fco.form_as_table_strict(form, display_fields)}
        <button class="btn" type="submit">保存</button>
    </form>
</div>
