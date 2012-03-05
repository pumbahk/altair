<%inherit file='../../layout_2col.mako'/>

<%
count = len(role.permissions)
per = count / 2
%>

<div class="row">
<h4 class="page-header">オペレータ情報</h4>
<div class="span5">
<table class="table table-striped">
    <tbody>
    %for perm in role.permissions[:per]:
    <tr>
        <td><span class="label label-info">${perm.permission}</span></td>
    </tr>
    %endfor
    </tbody>
</table>
</div>

<div class="span5">
<table class="table table-striped">
    <tbody>
    %for perm in role.permissions[per:]:
    <tr>
        <td><span class="label label-info">${perm.permission}</span></td>
    </tr>
    %endfor
    </tbody>
</table>
</span>

</div>
</div>
