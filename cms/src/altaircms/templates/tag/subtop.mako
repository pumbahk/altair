<%inherit file='../layout_2col.mako'/>
<%namespace name="co" file="components.mako"/>

<h2>${classifier} tag</h2>
${co.menutab(supported, classifier)}

<div class="row">
  <div class="span5">
	<form action="#" method="GET">
      <table class="table">
        <tbody>
          ${co.formfield(form, "classifier")}
          ${co.formfield(form, "query")}
        </tbody>
      </table>
	  <button type="submit" class="btn btn-primary"><i class="icon-cog icon-white"></i> Search</button>
    </form>
  </div>

  <div class="span5">
    <h3> 最近追加されたタグ</h3>
    ${co.new_tags(classifier, new_tags)}
  </div>
</div>

<div class="row">
  <h3>タグ一覧</h3>
<%
seq = h.paginate(request, tags, item_count=tags.count())
%>

  <table class="table">
	<thread>
	  <tr>
		<th span=>名前</th>
		<th>公開／非公開</th>
		<th>更新日時</th>
		<th>作成日時</th>
	  </tr>
	</thread>
	<tbody>
	  ${seq.pager()}
	  % for tag in seq.paginated():
	  <tr>
		<td>
		  <a href="${h.tag.to_search_query(request, classifier, tag)}">${tag.label}</a>
		</td>
		<td>${u"公開" if tag.publicp else u"非公開" }</td>
		<td>${tag.updated_at}</td>
		<td>${tag.created_at}</td>
	  </tr>
	  % endfor
	</tbody>
  </table>
  ${seq.pager()}
</div>
