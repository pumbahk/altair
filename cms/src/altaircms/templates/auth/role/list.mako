<%inherit file='../../layout_2col.mako'/>

<h4>ロール一覧</h4>
<table class="table table-striped">
    <thead>
    <tr>
        <th>Role</th>
        <th>Permissions</th>
        <td></td>
    </tr>
    </thead>
    <tbody>
    %for role in roles:
    <tr>
        <td>${role.name}</td>
        <td>
        %for perm in role.permissions:
          <span class="label label-info">${perm.name}</span>
        %endfor
        </td>
        <td><a href="${request.route_url("role", id=role.id)}"><span class="btn"><i class="icon-eye-open"> </i> Show</span></a></td>
    </tr>
    %endfor
    </tbody>
</table>