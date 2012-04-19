<%inherit file='../layout_2col.mako'/>
<h3>${ps.name}</h3>
<form>
  fieldset
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
  %for page in ps.pages:
  <tr>
    <td>${page.version}</td>
    <td>
      <a href="${request.route_url('page_edit_', page_id=page.id)}">${page.title}</a>
    </td>
    <td>${page.url}</td>
    <td>${page.publish_begin} 〜 ${page.publish_begin}</td>
    <td>表示中</td>
  </tr>
  %endfor
</table>
