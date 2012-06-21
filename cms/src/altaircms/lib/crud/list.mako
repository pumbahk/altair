<%inherit file='../../templates/layout_2col.mako'/>

<%namespace name="fco" file="../../templates/formcomponents.mako"/>
<%namespace name="nco" file="../../templates/navcomponents.mako"/>
<h2>${master_env.title}</h2>

<div class="row">
  <div class="span12">
    ${nco.breadcrumbs(
        names=["Top", master_env.title], 
        urls=[request.route_path("dashboard")])
    }
  </div>
</div>

<div class="row-fluid">
    <h3>${master_env.title}追加</h3>
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

${xs.pager()}
<table class="table table-striped">
  <thead>
    <tr>
      %for k in display_fields:
      <th>${getattr(form,k).label}</th>
      %endfor
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
              <a href="${request.route_path(master_env.join("update"),action="input",id=x.id)}" class="btn btn-small btn-primary">
                <i class="icon-cog icon-white"> </i> Update
              </a>
              <a href="${request.route_path(master_env.join("delete"),action="confirm",id=x.id)}" class="btn btn-small btn-danger">
                <i class="icon-trash icon-white"> </i> Delete
              </a>
              </td>
            </tr>
        %endfor
    </tbody>
</table>
${xs.pager()}
</div>
