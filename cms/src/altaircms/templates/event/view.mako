<%inherit file='../layout_2col.mako'/>
<%namespace name="nco" file="../navcomponents.mako"/>

<div class="row-fluid">
    ${nco.breadcrumbs(
        names=["Top", "Event", event.title],
        urls=[request.route_path("dashboard"), request.route_path("event_list")]
    )}


<h2>${event.title}</h2>

<table class="table table-striped">
      <tr>
        <th class="span2">タイトル</th><td>${event.title}</td>
      </tr>
      <tr>
        <th class="span2">サブタイトル</th><td>${event.subtitle}</td>
      </tr>
      <tr>
        <th class="span2">バックエンド管理番号</th><td>${event.backend_id}</td>
      </tr>
      <tr>
        <th class="span2">概要</th><td>${event.description}</td>
      </tr>
      <tr>
        <th>開催期間</th><td>${h.base.jterm(event.event_open,event.event_close)}</td>
      </tr>
      <tr>
        <th>販売期間</th><td>${h.base.jterm(event.deal_open,event.deal_close)}</td>
      </tr>
      <tr>
        <th class="span2">出演者</th><td>${event.performers}</td>
      </tr>
      <tr>
        <th class="span2">説明/注意事項</th><td>${event.notice}</td>
      </tr>
      <tr>
        <th class="span2">問い合わせ先</th><td>${event.inquiry_for}</td>
      </tr>
    </table>

  <div class="btn-group">
    <a href="${request.route_path("event_update",action="input",id=event.id)}" class="btn">
      <i class="icon-pencil"></i> 編集
    </a>
    <button class="btn dropdown-toggle" data-toggle="dropdown">
        <span class="caret"></span>
    </button>
    <ul class="dropdown-menu">
      <li>
        <a href="${request.route_path("event_update",action="input",id=event.id)}">
          <i class="icon-minus"></i> 編集
        </a>
      </li>
      <li>
        <a href="${request.route_path("event_create",action="input")}">
          <i class="icon-minus"></i> 新規作成
        </a>
      </li>
      <li>
        <a href="${request.route_path("event_delete",action="confirm",id=event.id)}">
          <i class="icon-minus"></i> 削除
        </a>
      </li>
    </ul>
  </div>

<hr/>

## たぶん。contextによってだしわける。
<h3>配下のページ一覧</h3>
  ## 一番下のjsに依存している
  ${myhelpers.pageset_describe_viewlet(request, event)}
<hr/>

<h3>パフォーマンス</h3>
  ## 一番下のjsに依存している
  ${myhelpers.performance_describe_viewlet(request,event)}
<hr/>

<h3>販売条件情報</h3>
  ## 一番下のjsに依存している
  ${myhelpers.sale_describe_viewlet(request,event)}

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
