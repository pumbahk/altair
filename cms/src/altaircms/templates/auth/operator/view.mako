<%inherit file='../../layout_2col.mako'/>

<h4 class="page-header">オペレータ情報</h4>
<table class="table">
    <tbody>
    <tr>
        <th>ID(Internal)</th>
        <td>${operator.id}</td>
    </tr>
    <tr>
        <th>ID(External)</th>
        <td>${operator.user_id}</td>
    </tr>
    <tr>
        <th>Authentication source</th>
        <td>${operator.auth_source}</td>
    </tr>
    <tr>
        <th>Role</th>
        <td>${u",".join([role.name for role in operator.roles])}</td>
    </tr>
    <tr>
        <th>最終ログイン</th>
        <td>${operator.last_login}</td>
    </tr>
    <tr>
        <th>登録日</th>
        <td>${operator.date_joined}</td>
    </tr>
    </tbody>
</table>

%if user.has_permission("operator_delete"):
    <form action="${request.route_path("operator", id=operator.id)}" method="POST">
        <input type="hidden" name="_method" value="delete"/>
        <button class="btn" type="submit">削除</button>
    </form>
%endif
