<%inherit file='../../layout_2col.mako'/>

<div class="row">
<h4>widget layout 一覧</h4>
<table class="table table-striped">
  <thead>
	<tr>
	  <th>タイトル</th><th>保存方法</th><th>全ての人に公開</th><th>作成者</th><th>作成日時</th><th>削除</th>
	</tr>
  </thead>
  <tbody>
    %for d in ds:
       <tr>
         ##<td><a href="#">${d.title}</a></td>
		 <td>${d.title}</td>
		 <td>${d.save_type}</td>
         <td>${u"公開" if d.is_public else u"-"}</td>
         <td> ${d.owner.screen_name if d.owner else "-"}</td>
         <td>${d.created_at}</td>
		 <td>
		   <form action="${h.widget.to_disposition_alter(request,d)}" method="POST">
             <input type="hidden" name="disposition" value="${d.id}"/>
			 <button type="submit" class="btn btn-danger"><i class="icon-trash icon-white"></i>delete</button>
		   </form>
		 </td>
       </tr>
    %endfor
  </tbody>
</table>
</div>
