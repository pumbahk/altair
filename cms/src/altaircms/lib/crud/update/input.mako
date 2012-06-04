<%inherit file='../../../templates/layout_2col.mako'/>

<%namespace name="fco" file="../../../templates/formcomponents.mako"/>

<div class="row">
    <h3>${master_env.title}更新</h3>
    <form action="${master_env.flow_api.next_flow_path(request)}" method="POST">
       ${fco.form_as_table_strict(form, display_fields)}
        <button class="btn" type="submit">保存</button>
    </form>
</div>
