<%inherit file='../../templates/layout_2col.mako'/>

<%namespace name="fco" file="../../templates/formcomponents.mako"/>
<%namespace name="nco" file="../../templates/navcomponents.mako"/>

<%block name="style">
<style type="text/css">
  .row-fluid h3 { margin-top:20px;  }
  .row-fluid h3.first { margin-top:0px;  }
</style>
</%block>

<h2>${master_env.title}</h2>

<div class="row-fluid">
  <div class="span12">
    ${nco.breadcrumbs(
        names=["Top", master_env.title], 
        urls=[request.route_path("dashboard")])
    }
  </div>
</div>

<div class="row-fluid">
    <h3 class="first">${master_env.title}追加</h3>
    <a href="${request.route_path(master_env.join("create"), action="input")}"  class="btn btn-success btn-large">新しい${master_env.title}を作成する</a>

    %if query_form:
      <h3>絞り込み検索</h3>
       <form class="well" action="#" method="GET">
         %for k in query_form.data.keys():
           ${getattr(query_form,k).label.text} ${getattr(query_form, k)}
         %endfor
           <input type="hidden" name="query" value="true">
           <button class="btn btn-small btn-info"><i class="icon-search icon-white"></i> search</button>
       </form>
    %endif
</div>

<div class="row-fluid">
<h3>${master_env.title}一覧</h3>

<p>全${xs.opts.get("item_count") or xs.collection.count()}件</p>
${xs.pager()}
<table class="table table-striped">
  <thead>
    <tr>
      %for k in display_fields:
      <th>${getattr(form,k).label}</th>
      %endfor
	  <th>操作</th>
    </tr>
  </thead>
    <tbody>
        %for x in xs.paginated():
            <%
             x = master_env.mapper(request, x) if master_env.mapper else x
             %>
            <tr>
              %for k in display_fields:
                <td>${getattr(x,k, "-")}</td>
              %endfor
              <td>
				<div class="btn-group">
				  <button class="btn dropdown-toggle" data-toggle="dropdown">
					<span class="caret"></span>
				  </button>
				  <ul class="dropdown-menu">
					<li>
					  <a href="${request.route_path(master_env.join("update"),action="input",id=x.id)}">
						<i class="icon-cog"> </i> 編集
					  </a>
					</li>
					<li>
					  <a href="${request.route_path(master_env.join("create"), action="copied_input",_query=dict(id=x.id))}">
						<i class="icon-cog"> </i> コピーして新規作成
					  </a>
					</li>
					<li>
					  <a href="${request.route_path(master_env.join("delete"),action="confirm",id=x.id)}">
						<i class="icon-trash"> </i> 削除
					  </a>
					</li>
				  </ul>
				</div>
              </td>
            </tr>
        %endfor
    </tbody>
</table>
${xs.pager()}
</div>
