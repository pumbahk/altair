<%inherit file='../../../templates/layout_2col.mako'/>

<%namespace name="fco" file="../../../templates/formcomponents.mako"/>
<%namespace name="nco" file="../../../templates/navcomponents.mako"/>

<h2>${master_env.title} 新規作成</h2>

<div class="row-fluid">
  <div class="span10">
    ${nco.breadcrumbs(
        names=["Top", u"新規作成"], 
        urls=[request.route_path("dashboard"),])
    }
  </div>
</div>

<div class="row-fluid">
    <h3>${master_env.title}追加</h3>
    <form action="${master_env.flow_api.next_flow_path(request)}" method="POST">
       ${fco.form_as_table_strict(form, display_fields)}
        <button class="btn" type="submit">保存</button>
    </form>
</div>
