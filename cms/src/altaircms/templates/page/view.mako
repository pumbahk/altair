<%inherit file='../layout_2col.mako'/>
<%namespace name="co" file="./components.mako"/>
<%namespace name="nco" file="../navcomponents.mako"/>
<%namespace name="fco" file="../formcomponents.mako"/>
<%namespace name="mco" file="../modelcomponents.mako"/>
<%namespace name="gadgets" file="../gadgets.mako"/>

<div class="row-fluid">
    ${nco.breadcrumbs(
        names=["Top", "Event", page.event.title, page.name],
        urls=[request.route_path("dashboard"),
              request.route_path("event_list"),
              request.route_path("event", id=page.event.id)
              ]
    )}

<h2>${page.name}</h2>
	  <%
parent = page.pageset.parent
event = page.event or page.pageset.event
%>
    <table class="table table-striped">
      <tr>
        <th class="span2">ページ名</th>
		<td>
		  ${page.title}
 		  <a target="_blank" href="${request.route_path("preview_page", page_id=page.id)}"><i class="icon-eye-open"> </i></a>
		</td>
      </tr>
      <tr>
        <th class="span2">所属イベント</th><td><a href="${h.page.event_page(request,page)}">${page.event.title if page.event else ""}</a></td>
      </tr>
      <tr>
        <th class="span2">親ページ</th>
		<td>
		  %for p in reversed(page.pageset.ancestors if page.pageset else []):
			<a class="parent" href="${request.route_path("pageset", pageset_id=p.id)}">${p.name}</a> &raquo;
          %endfor
        </td>
      </tr>
      <tr>
        <th class="span2">タイトル</th><td>${page.title}</td>
      </tr>
      <tr>
        <th class="span2">description</th><td>${page.description}</td>
      </tr>
      <tr>
        <th class="span2">キーワード</th><td>${page.keywords}</td>
      </tr>
      <tr>
	<th>掲載期間</th>
	<td>　${h.base.jterm(page.publish_begin, page.publish_end)}</td>
      </tr>
      <tr>
        <th class="span2">公開ステータス</th><td>${h.page.show_publish_status(page)}</td>
      </tr>
    </table>

  <div class="btn-group" style="margin-bottom:20px;">
    <a target="_blank" href="${request.route_path("page_update",id=page.id)}" class="btn">
      <i class="icon-pencil"></i> ページ基本情報編集
    </a>
    <button class="btn dropdown-toggle" data-toggle="dropdown">
        <span class="caret"></span>
    </button>
    <ul class="dropdown-menu">
      <li>
		<a target="_blank" href="${request.route_path("page_edit_", page_id=page.id)}"><i class="icon-minus"></i> ページのレイアウト編集</a>
      </li>
	  <li class="divider"></li>
	  <li>
	   	<a target="_blank" href="${request.route_path("preview_page", page_id=page.id)}"><i class="icon-eye-open"></i>Preview</a>
	  </li>
    </ul>
  </div>

<h3>設定されているタグ</h3>
<div class="box">
  <table class="table">
	<thead>
	  <tr>
		<th>タグの種類</th><th></th><th>タグの種類</th><th>作成日時</th><th>更新日時</th>
	  </tr>
	</thead>
	<tbody>
<%
tags = page.public_tags
tagsize = len(tags)
%>
	  <tr>
		<td rowspan="${tagsize}">公開タグ</td>
		%if tags:
		<td>
          <input type="checkbox" name="object_id" value="${tags[0].id}">
		</td>
		  <td>${tags[0].label}</td>
		  <td>${h.base.jdate(tags[0].created_at)}</td>
		  <td>${h.base.jdate(tags[0].updated_at)}</td>
		%endif
	  </tr>
	  %if tagsize >1:
	  %for tag in tags[1:]:
	  <tr>
		<td>
          <input type="checkbox" name="object_id" value="${tag.id}">
		</td>
		<td>${tag.label}</td>
		<td>${h.base.jdate(tag.created_at)}</td>
		<td>${h.base.jdate(tag.updated_at)}</td>
	  </tr>
	  %endfor
	  %endif
<%
tags = page.private_tags
tagsize = len(tags)
%>
	  <tr>
		<td rowspan="${tagsize}">非公開タグ</td>
		%if tags:
		  <td>
			<input type="checkbox" name="object_id" value="${tags[0].id}">
		  </td>
		  <td>${tags[0].label}</td>
		  <td>${h.base.jdate(tags[0].created_at)}</td>
		  <td>${h.base.jdate(tags[0].updated_at)}</td>
		%endif
	  </tr>
	  %if tagsize >1:
	  %for tag in tags[1:]:
	  <tr>
		<td>
          <input type="checkbox" name="object_id" value="${tag.id}">
		</td>
		<td>${tag.label}</td>
		<td>${h.base.jdate(tag.created_at)}</td>
		<td>${h.base.jdate(tag.updated_at)}</td>
	  </tr>
	  %endfor
	  %endif
	</tbody>
  </table>
  <div class="btn-group">
    <a href="${request.route_path("performance_update",action="input",id="__id__")}" class="btn action">
      <i class="icon-pencil"></i> タグの追加
    </a>
    <button class="btn dropdown-toggle" data-toggle="dropdown">
        <span class="caret"></span>
    </button>
    <ul class="dropdown-menu">
      <li>
        <a href="${request.route_path("performance_update",action="detail",id="__id__")}" class="action">
          <i class="icon-pencil"></i> 詳細画面
        </a>
      </li>
      <li>
        <a href="${request.route_path("performance_update",action="input",id="__id__")}" class="action">
          <i class="icon-minus"></i> 編集
        </a>
      </li>
      <li>
        <a href="${request.route_path("performance_create",action="input")}">
          <i class="icon-minus"></i> 新規作成
        </a>
      </li>
      <li>
        <a href="${request.route_path("performance_delete",action="confirm",id="__id__")}" class="action">
          <i class="icon-minus"></i> 削除
        </a>
      </li>
      <li class="divider"></li>
      <li>${ gadgets.getti_update_code_button()}</li>
    </ul>
  </div>

</div>
<h3>ホットワード</h3>
<h3>アクセスキー</h3>
<h3>アセット</h3>

</div>


