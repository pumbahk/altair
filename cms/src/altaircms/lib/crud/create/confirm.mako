<%inherit file='../../../templates/layout_2col.mako'/>

<%namespace name="fco" file="../../../templates/formcomponents.mako"/>

<%def name="form_to_table(form, x)">
<table class="table table-striped">
  <tbody>
  % for k in display_fields:
    <tr>
	  <td>${getattr(form,k).label}</td>
	  <td>${getattr(x,k)}</td>
	</tr>
  % endfor
  </tbody>
</table>
</%def>

<div class="row">
    <h3>${master_env.title}追加 確認画面</h3>

	<div class="alert alert-info">
	  以下の内容の${master_env.title}を作成します。良いですか？
	</div>

	${form_to_table(form, master_env.mapper(request, obj))}

    <form action="${master_env.flow_api.next_flow_path(request)}" method="POST">
       ${fco.postdata_as_hidden_input(request.POST)}
        <button class="btn" type="submit">保存</button>
    </form>
</div>
