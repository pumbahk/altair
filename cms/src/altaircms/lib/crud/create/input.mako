<%inherit file='../../templates/layout_2col.mako'/>

<%namespace name="fco" file="../../templates/formcomponents.mako"/>

<div class="row">
    <h3>${context.title}追加</h3>
    <form action="${request.next_flow_path(request)}" method="POST">
       ${fco.form_as_table_strict(form, display_fields)}
        <button class="btn" type="submit">保存</button>
    </form>
</div>
