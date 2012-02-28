<%inherit file='../layout_2col.mako'/>
<div class="row">
    <div class="span6">
        <h4>レイアウト</h4>
        <form action="#" method="POST">
            <%include file="../parts/formerror.mako"/>
        <table class="table">
            <tbody>
            <tr>
                <th>${form.title.label}</th><td>${form.title}</td>
            </tr>
            <tr>
                <th>${form.blocks.label}</th><td>${form.blocks}</td>
            </tr>
            <tr>
                <th>${form.template_filename.label}</th><td>${form.template_filename}</td>
            </tr>
            </tbody>
        </table>
            <button class="btn" type="submit">保存</button>
        </form>
    </div>
</div>

<hr/>

<div class="row">
    <ul class="nav nav-list">
        <li class="nav-header">登録済みレイアウト</li>
        %for layout in layouts['layouts']:
                <li><a href="${request.route_url('layout', layout_id=layout['id'])}">${layout['title']}</a></li>
        %endfor
    </ul>
</div>