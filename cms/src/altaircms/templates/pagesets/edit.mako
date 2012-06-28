<%inherit file='../layout_2col.mako'/>
<h3>${ps.name}</h3>
<form action="${request.url}" method="POST">
${form.errors}
<table>
  <tr>
    <th>URL</th>
    <td>${ps.url}</td>
  </tr>
</table>

<hr />

<h4>ページ</h4>
<table class="table">
  <tr>
    <td>#</td>
    <td>名前</td>
    <td>URL</td>
    <td>作成日時</td>
    <td>期間</td>
    <td>現在表示状況</td>
  </tr>
  %for page in ps.sorted_pages:
  <tr>
    <td>${page.version}</td>
    <td>
      <a href="${request.route_url('page_edit_', page_id=page.id)}">${page.name}</a>
    </td>
    <td>${page.url}</td>
    <td>${page.created_at}</td>
    <td>${f.publish_begin(form, page)} 〜 ${f.publish_end(form, page)}</td>
    <td>
	    ${f.published(form, page)}
        <div class="btn-group">
          <a class="btn dropdown-toggle" data-toggle="dropdown" href="#">
            ${u"公開中" if page.published else u"非公開"}
            <span class="caret"></span>
          </a>
          <ul class="dropdown-menu">
            <!-- dropdown menu links -->
            <li><a href="${request.route_path("api_page_publish_status", status="publish", page_id=page.id)}" class="publish_status">公開する</a></li>
            <li><a href="${request.route_path("api_page_publish_status", status="unpublish", page_id=page.id)}" class="publish_status">非公開にする</a></li>
          </ul>
        </div>
    </td>
  </tr>
  %endfor
</table>
<button type="submit" class="btn btn-primary">期間変更する</button>
</form>

<script type="text/javascript">
  $(function(){
  // swap status
	$(".publish_status").click(function(e){
	  e.preventDefault();
	  if(window.confirm("ステータスを「"+$(this).text()+"」に変更しますがよろしいですか？")){
		$.post($(this).attr("href")).done(function(){location.reload();});
	  }
	});
  });
</script>

