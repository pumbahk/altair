<%inherit file='../layout_2col.mako'/>

<div>
    <h1 class="page-header">レイアウト - ${layout}</h1>
</div>

<div class="row">
    <div class="span6">
    <table class="table table-striped">
        <tbody>
        <tr>
            <th>ID</th>
            <td>${layout.id}</td>
        </tr>
        <tr>
            <th>タイトル</th>
            <td>${layout.title}</td>
        </tr>
        <tr>
            <th>ブロック</th>
            <td>${layout.blocks}</td>
        </tr>
        <tr>
            <th>テンプレートファイル名</th>
            <td>${layout.template_filename}</td>
        </tr>
        </tbody>
    </table>
    </div>
</div>