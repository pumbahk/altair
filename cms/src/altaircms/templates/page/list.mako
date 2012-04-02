<%inherit file='../layout_2col.mako'/>
<%block name='style'>
<style type="text/css">
  .alert{ margin:1%  }
  .size1{ width:100%;  }
  .size2{ width:34.5%; }
  .size3{ width:17.8%; }
  .left{ float:left; }
  .clear{ clear:both; }
</style>
</%block>

<script type="text/javascript">
  var render_demo = function(){
    var layout_id = $(this).val();
    $("#layout_demo").load("${request.route_path("layout_demo")}"+"?id="+layout_id);
  };

  $(function(){
    $("[name='layout']").live("change", render_demo);
  });
</script>

<div class="row">
    <div class="span5">
      <h3>ページ追加・一覧</h3>
	</div>
    <div class="span5">
      <h3>layout image</h3>
	</div>
    <div class="span5">
    <%include file="../parts/formerror.mako"/>
    <form action="#" method="POST">
        <table class="table">
            <tbody>
            <tr>
                <th>${form.url.label}</th><td>${form.url}</td>
            </tr>
            <tr>
                <th>${form.title.label}</th><td>${form.title}</td>
            </tr>
            <tr>
                <th>${form.description.label}</th><td>${form.description}</td>
            </tr>
            <tr>
                <th>${form.keywords.label}</th><td>${form.keywords}</td>
            </tr>
##            <tr>
##                <th>${form.structure.label}</th><td>${form.structure}</td>
##            </tr>
            <tr>
                <th>${form.layout.label}</th><td>${form.layout}</td>
            </tr>
            </tbody>
        </table>
        <button class="btn" type="submit">保存</button>
    </form>
	</div>
	<div class="span5" id="layout_demo">
	</div>
</div>

<div class="row">
<h4>ページ一覧</h4>
<table class="table table-striped">
    <tbody>
        %for page in pages:
            <tr>
                <td>${page.created_at}</td>
                <td>${page.url}</td>
                <td><a href="${request.route_path("page_edit_", page_id=page.id)}">${page.title}</a></td>
                <td>
                    <a href="${h.front.to_preview_page(request, page)}" class="btn btn-small"><i class="icon-eye-open"> </i> Preview</a>
                </td>
            </tr>
        %endfor
    </tbody>
</table>
</div>
