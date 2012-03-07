<%inherit file='../../layout_2col.mako'/>

<h4>APIKEYの追加</h4>
<div class="row">
<div class="span4">
<form action="${request.route_url("apikey_list")}" method="POST">
${form.name}<br/>
<button type="submit" class="btn"><i class="icon-plus"> </i> Add</button>
</form>
</div>
</div>

<hr/>
<h4>APIKEY一覧</h4>
<div class="row">
<div class="span10">
<table class="table table-striped">
    <thead>
    <tr>
        <th>ID</th>
        <th>Name</th>
        <th>APIKEY</th>
        <td></td>
    </tr>
    </thead>
    <tbody>
    %if apikeys.count():
    %for apikey in apikeys:
    <tr>
        <td>${apikey.id}</td>
        <td>${apikey.name}</td>
        <td>${apikey.apikey}</td>
        <td>
        <form action="${request.route_url("apikey", id=apikey.id)}" method="POST">
        <input type="hidden" name="_method" value="delete"/>
        <button class="btn"><i class="icon-trash"> </i> Delete</button>
        </td>
    </tr>
    %endfor
    %else:
    <tr>
        <td colspan="3">登録済みのAPIKEYはありません。</td>
    </tr>
    %endif
    </tbody>
</table>
</div>
</div>