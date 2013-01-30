<%inherit file='../layout_2col.mako'/>
<%namespace name="gadgets" file="../gadgets.mako"/>
<%namespace name="nco" file="../navcomponents.mako"/>

<div class="row-fluid">
    ${nco.breadcrumbs(
        names=["Top", "Event",u"イベント:%s" % event.title, performance.title],
        urls=[request.route_path("dashboard"), request.route_path("event_list"), request.route_path("event", id=event.id)]
    )}

    
<h2>${performance.title}</h2>

<table class="table table-striped">
  <tbody>
  % for k in display_fields:
    <tr>
      <th class="span2">${getattr(form,k).label}</th>
      <td>${ getattr(mapped, k)}</td>
    </tr>
  % endfor
  </tbody>
</table>

  <div class="btn-group">
    <a href="${request.route_path("performance_update",action="input",id=performance.id)}" class="btn">
      <i class="icon-pencil"></i> 編集
    </a>
    <button class="btn dropdown-toggle" data-toggle="dropdown">
        <span class="caret"></span>
    </button>
    <ul class="dropdown-menu">
      <li>
        <a href="${request.route_path("performance_update",action="input",id=performance.id)}">
          <i class="icon-minus"></i> 編集
        </a>
      </li>
      <li>
        <a href="${request.route_path("performance_create",action="input")}">
          <i class="icon-minus"></i> 新規作成
        </a>
      </li>
      <li>
        <a href="${request.route_path("performance_delete",action="confirm",id=performance.id)}">
          <i class="icon-minus"></i> 削除
        </a>
      </li>
    </ul>
  </div>


## getti
<hr/>
<h3>getti購入リンク設定</h3>
<p>同一グループの公演の購入先リンクをgettiの登録コードを指定することで登録できます。</p>

<form action="register_get">
<table class="table">
  <thead>
    <tr>
##    <th></th>
      <th>イベント</th><th>公演</th><th>バックエンドid</th><th>公演日開始</th><th>場所</th><th>pc購入URL</th><th>mobile購入URL</th>
    </tr>
  </thead>
<tbody>
    <tr>
<%
performances = event.performances
performances_size = len(performances)
%>
##        <td><input type="checkbox" name="performance:${performances[0].id}" value="${performances[0]}.id}"></td>
        <td rowspan="${performances_size}">${event.title}</td>
        <td>${performances[0].title}</td>
        <td>${performances[0].backend_id}</td>
        <td>${performances[0].venue}</td>
        <td>${h.base.jdate(performances[0].start_on)}</td>
        <td>${performances[0].purchase_link or u"-"}</td>
        <td>${performances[0].mobile_purchase_link or u"-"}</td>
      </tr>
    %for p in performances[1:]:
      <tr>
##      <td><input type="checkbox" name="performance:${p.id}" value="${p.id}"></td>
        <td>${p.title}</td>
        <td>${p.backend_id}</td>
        <td>${p.venue}</td>
        <td>${h.base.jdate(p.start_on)}</td>
        <td>${p.purchase_link or u"-"}</td>
        <td>${p.mobile_purchase_link or u"-"}</td>
      </tr>
    %endfor
</tbody>
</table>
</div>

${gadgets.getti_update_code(performances,"getti_submit")}
${ gadgets.getti_update_code_button()}
