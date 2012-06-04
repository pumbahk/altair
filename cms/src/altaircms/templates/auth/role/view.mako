<%inherit file='../../layout_2col.mako'/>

<%
count = len(role.permissions)
per = count / 2
%>

<h4>${role.name}の権限一覧</h4>

<div class="row">
<div class="span4">
<form action="${request.route_path("role", id=role.id)}" method="POST">
${form.permission}<br/>
<button class="btn"><i class="icon-plus"> </i> Add</buton>
</form>
</div>
</div>


<div class="row">
<div class="span5 pull-left">
<table class="table table-striped">
    <tbody>
    %for perm in role.permissions[:per]:
    <tr>
        <td>
            <span class="label label-info">${perm}</span>
            <span class="pull-right">
                <form action="${request.route_path("role_permission", role_id=role.id, id=perm)}" method="POST">
                <input type="hidden" name="_method" value="delete"/>
                <button type="submit" class="btn btn-small"><i class="icon-trash"> </i> Delete</button>
                </form>
            </span>
        </td>
    </tr>
    %endfor
    </tbody>
</table>
</div>

<div class="span5 pull-left">
<table class="table table-striped">
    <tbody>
    %for perm in role.permissions[per:]:
    <tr>
        <td>
            <span class="label label-info">${perm}</span>
            <span class="pull-right">
                <form action="${request.route_path("role_permission", role_id=role.id, id=perm)}" method="POST">
                <input type="hidden" name="_method" value="delete"/>
                <button type="submit" class="btn btn-small"><i class="icon-trash"> </i> Delete</button>
                </form>
            </span>
        </td>
    </tr>
    %endfor
    </tbody>
</table>
</span>

</div>
</div>
