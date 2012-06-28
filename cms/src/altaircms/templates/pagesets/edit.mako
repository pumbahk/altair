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
    <td>タイトル</td>
    <td>URL</td>
    <td>期間</td>
    <td>現在表示状況</td>
  </tr>
  %for page in ps.sorted_pages:
  <tr>
    <td>${page.version}</td>
    <td>
      <a href="${request.route_url('page_edit_', page_id=page.id)}">${page.title}</a>
    </td>
    <td>${page.url}</td>
    <td>${f.publish_begin(form, page)} 〜 ${f.publish_end(form, page)}</td>
    <td>表示中</td>
  </tr>
  %endfor
</table>
<button type="submit" class="btn">Update</button>
</form>
