<%inherit file='../layout_2col.mako'/>


<div class="row">
    <h4>APIKEY新規登録</h4>

    <div class="span8">
        <form action="${request.route_url("apikey_list")}" method="POST">
            <table class="table">
                <tbody>
                <tr>
                    <td>${form.name.label}</td>
                    <td>${form.name}
                        <button class="btn" type="submit"><i class="icon-plus"> </i>追加</button>
                        %if form.name.errors:
                            <div>
                                %for error in form.name.errors:
                                    <span class="label label-warning">${error}</span>
                                %endfor
                            </div>
                        %endif
                    </td>
                </tr>
                </tbody>
            </table>
        </form>
    </div>
</div>

<div class="row">
    <h4>APIKEY一覧</h4>
    <table class="table">
        <thead>
        <tr>
            <th>Name</th>
            <th>APIKEY</th>
            <td></td>
        </tr>
        </thead>
        <tbody>
        %for apikey in apikeys:
                <tr>
                    <td>${apikey.name}</td>
                    <td>${apikey.apikey}</td>
                    <td><span><a class="btn btn-small" href="#"><i class="icon-eye-open"> </i> Show</a></span></td>
                </tr>
        %else:
            <tr><td colspan="3">登録済みAPIKEYはありません。</td></tr>
        %endfor
        </tbody>
    </table>
</div>
