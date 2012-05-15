<%inherit file='../../templates/layout_2col.mako'/>

<%namespace name="fco" file="../../templates/formcomponents.mako"/>

<div class="row">
    <h3>${context.title}追加 確認画面</h3>
	${fco.form_to_table(form)}

    <form action="${request.next_flow_path(request)}" method="POST">
       ${fco.postdata_as_hidden_input(request.POST)}
        <button class="btn" type="submit">保存</button>
    </form>
</div>
