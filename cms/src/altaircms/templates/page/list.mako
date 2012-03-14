<%inherit file='../layout_2col.mako'/>

<div class="row">
    <h3>ページ追加・一覧</h3>
    <%include file="../parts/formerror.mako"/>
    <form action="#" method="POST">
        <table class="table">
            <tbody>
            <tr>
                <th>${form.url.label}</th><td>${form.url}</td>
            </tr>
            <tr>
                <th>${form.title.label}</th><td>${form.title}</td>
            </tr>
            <tr>
                <th>${form.description.label}</th><td>${form.description}</td>
            </tr>
            <tr>
                <th>${form.keywords.label}</th><td>${form.keywords}</td>
            </tr>
            <tr>
                <th>${form.structure.label}</th><td>${form.structure}</td>
            </tr>
            <tr>
                <th>${form.layout_id.label}</th><td>${form.layout_id}</td>
            </tr>
            </tbody>
        </table>
        <button class="btn" type="submit">保存</button>
    </form>
</div>

<div class="row">
<h4>ページ一覧</h4>
<table class="table table-striped">
    <tbody>
        %for page in pages:
            <tr>
                <td>${page.created_at}</td>
                <td>${page.url}</td>
                <td><a href="${request.route_path("page_edit_", page_id=page.id)}">${page.title}</a></td>
                <td>
                    <a href="${h.front.to_preview_page(request, page)}" class="btn btn-small"><i class="icon-eye-open"> </i> Preview</a>
                </td>
            </tr>
        %endfor
    </tbody>
</table>
</div>
