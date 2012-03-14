<%inherit file='../../layout_2col.mako'/>

<h4>オペレータ一覧</h4>
<table class="table table-striped">
    <thead>
    <tr>
        <th>ID(Internal)</th>
        <th>ID(OAuth)</th>
        <th>Authentication source</th>
        <th>Screen name</th>
        <th>Role</th>
        <td></td>
    </tr>
    </thead>
    <tbody>
    %for operator in operators:
    <tr>
        <td>${operator.id}</td>
        <td>${operator.user_id}</td>
        <td>${operator.auth_source}</td>
        <td>${operator.screen_name}</td>
        <td>${operator.role.name}</td>
        <td><a href="${request.route_path("operator", id=operator.id)}"><span class="btn"><i class="icon-eye-open"> </i> Show</span></a></td>
    </tr>
    %endfor
    </tbody>


</table>
