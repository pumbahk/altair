<%inherit file='altaircms:templates/layout_2col.mako'/>

<%namespace name="fco" file="altaircms:templates/formcomponents.mako"/>
<%namespace name="nco" file="altaircms:templates/navcomponents.mako"/>
<link href="/static/css/jquery.cleditor.css" rel="stylesheet" type="text/css"></link>
<script type="text/javascript" src="/static/js/jquery.cleditor.min.js"></script>

<script type="text/javascript">
  $(function(){
   $("#text").cleditor();
  });
</script>

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
    <form action="${request.current_route_path(action="confirm")}" method="POST">
       ${fco.form_as_table_strict(form, display_fields)}
        <button class="btn" type="submit">保存</button>
    </form>
</div>
