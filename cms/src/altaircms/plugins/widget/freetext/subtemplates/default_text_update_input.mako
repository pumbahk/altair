<%inherit file='altaircms:templates/layout_2col.mako'/>

<%namespace name="fco" file="altaircms:templates/formcomponents.mako"/>

<link href="/static/css/jquery.cleditor.css" rel="stylesheet" type="text/css"></link>
<script type="text/javascript" src="/static/js/jquery.cleditor.min.js"></script>

<script type="text/javascript">
  $(function(){
   $("#text").cleditor();
  });
</script>

<div class="row">
    <h3>${master_env.title}更新</h3>
    <form action="${master_env.flow_api.next_flow_path(request)}" method="POST">
       ${fco.form_as_table_strict(form, display_fields)}
        <button class="btn" type="submit">保存</button>
    </form>
</div>
