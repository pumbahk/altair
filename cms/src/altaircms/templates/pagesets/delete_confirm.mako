<%inherit file='../layout_2col.mako'/>
<%namespace name="nco" file="../navcomponents.mako"/>

<h2>削除確認画面 ${pageset.name}</h2>

<div class="row-fluid">
  <div class="span10">
    ${nco.breadcrumbs(
	    names=["Top", pageset.name, u"削除"], 
	    urls=[request.route_path("dashboard"),
	          h.link.pageset_detail(request,pageset),
              h.page.to_edit_page(request,pageset)]
	)}
  </div>
</div>

<div class="alert alert-error">
  以下の内容のページセットを削除します。良いですか？
  (結びついているページが全て消えます!)
</div>

<h3>ページ一覧</h3>
<div id="pageset_items">
  ${myhelpers.pageset_describe_viewlet(request, pageset)}
</div>
<hr/>

<form action="#" method="POST">
  <input id="_method" name="_method" type="hidden" value="delete" />
  <button type="submit" class="btn btn-danger"><i class="icon-trash icon-white"></i> Delete</button>
</form>        

<script type="text/javascript">
  $(function(){$("#pageset_items input:radio,.btn-group").css("display", "none");});
</script>
