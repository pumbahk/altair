<%inherit file='../layout_2col.mako'/>
<%namespace name="nco" file="../navcomponents.mako"/>
<%namespace name="fco" file="../formcomponents.mako"/>
<%namespace name="mco" file="../modelcomponents.mako"/>
<%namespace name="gadgets" file="../gadgets.mako"/>

<%block name="style">
<style type="text/css">
#appendix h3{ 
  margin-top:20px;
}
</style>
</%block>


<div class="row-fluid">
    ${nco.breadcrumbs(
        names=["Top", "Page", pageset.name],
        urls=[request.route_path("dashboard"), request.route_path("pageset_list", kind="other")]
    )}


<h2>${pageset.name}</h2>

<table class="table table-striped">
  <tr>
    <th class="span2">ページ名</th><td>${pageset.name}</td>
  </tr>
  <tr>
    <th class="span2">URL</th><td>${pageset.url}</td>
  </tr>
  <tr>
    <th class="span2">ページタイプ</th><td>その他</td>
  </tr>
  <tr>
    <th class="span2">ページカテゴリ</th><td>${pageset.category.label if pageset.category else u""}</td>
  </tr>
</table>

  <div class="btn-group">
    <a href="#" class="btn">
      <i class="icon-pencil"></i> ページセットの編集
    </a>
    <button class="btn dropdown-toggle" data-toggle="dropdown">
        <span class="caret"></span>
    </button>
    <ul class="dropdown-menu">
      <li>
        <a href="${request.route_path("pageset_delete", pageset_id=pageset.id)}">
          <i class="icon-trash"></i> ページセットの削除
        </a>
      </li>
      <li>
        <a href="#">
          <i class="icon-minus"></i> ページセットの編集
        </a>
      </li>
    </ul>
  </div>

<hr/>

<h3>ページ一覧</h3>
  ## 一番下のjsに依存している
<div id="pageset_items">
  ${myhelpers.pageset_describe_viewlet(request, pageset)}
</div>
<script type="text/javascript">
  $(function(){$("#pageset_items input:radio, #pageset_items .btn-group").css("display", "none");});
</script>
<hr/>

<h3>登録しているアセット</h3>
  ${myhelpers.asset_describe_viewlet(request,pageset)}
<hr/>

<h3>画像なしトピック</h3>
  ${myhelpers.topic_describe_viewlet(request,pageset)}
<hr/>

<h3>画像付きトピック</h3>
  ${myhelpers.topcontent_describe_viewlet(request,pageset)}
<hr/>

<script type="text/javascript">
  $(function(){
   $(".box .btn-group a.action").click(function(){
      var  pk = $(this).parents(".box").find("input[name='object_id']:checked").val();
      if(!pk){ console.log("sorry"); return false; }

      // initialize
      var $this = $(this);
      if (!$this.data("href-fmt")){
        $this.data("href-fmt", this.href);
      }
      this.href = $this.data("href-fmt").replace("__id__", pk);
      return true;;
    });
  })
</script>

</div>
