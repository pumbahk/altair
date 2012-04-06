## todo refactoring
<%def name="menutab(supported, classifier=None)">
<div class="row">
  <ul class="nav nav-tabs">
	% if classifier is None:
   	    <li class="active"><a href="${h.tag.to_search(request)}">top</a></li>
	% else:
  	    <li><a href="${h.tag.to_search(request)}">top</a></li>
	% endif

    % for k in supported:
      % if classifier==k:
   	    <li class="active"><a href="${h.tag.to_search(request,k)}">${k}</a></li>
      % else:
   	    <li><a href="${h.tag.to_search(request,k)}">${k}</a></li>
      % endif
    % endfor
  </ul>
</div>
</%def>

<%def name="new_tags(classifier, new_tags)">
<div class="row">
  <div class="span10">
    <ul>
      %for tag in new_tags:
        <li><a href="${h.tag.to_search_query(request, classifier, tag)}">${tag.label}</a>(${h.tag.show_public_status(tag)} ${tag.updated_at})</li>
      %endfor
    </ul>
    <table class="table">
    </table>
  </div>
</div>
</%def>

<%def name="formfield(form, k)">
	<tr><th>${getattr(form,k).label}</th><td>${getattr(form,k)}
	%if k in form.errors:
	  <br/>
	  %for error in form.errors[k]:
		<span class="btn btn-danger">${error}</span>
	  %endfor
	%endif
	</td></tr>
</%def>

<%def name="page_search_result(request, query_result)">
  <thead>
	<tr>
	  <th>タイトル</th>
	  <th>URL</th>
	  <th>イベント</th>
	  <th>概要</th>
	  <th>更新日時</th>
	</tr>
  </thead>
	<tbody>
	  % for page in query_result:
		<tr>
		  <td>${page.title}</td>
		  <td>${page.url}</td>
		  <td>${page.event.title if page.event else u"-"}</td>
		  <td>${page.description[:20] if len(page.description) > 20 else page.description}</td>
		  <td>${page.updated_at}</td>
		</tr>
	  % endfor
	</tbody>
</%def>

<%def name="event_search_result(request, query_result)">
  <thead>
	<tr>
	  <th>タイトル</th>
	  <th>更新日時</th>
	</tr>
  </thead>
	<tbody>
	  % for event in query_result:
		<tr>
		  <td>${event.title}</td>
		  <td>${event.updated_at}</td>
		</tr>
	  % endfor
	</tbody>
</%def>

<%def name="asset_search_result(request, query_result)">
  <thead>
	<tr>
	  <th>path</th>
	  <th>更新日時</th>
	</tr>
  </thead>
	<tbody>
	  % for asset in query_result:
		<tr>
		  <td>${asset.filepath}</td>
		  <td>${asset.updated_at}</td>
		</tr>
	  % endfor
	</tbody>
</%def>
