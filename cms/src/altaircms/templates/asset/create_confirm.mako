<%inherit file='../layout_2col.mako'/>
<%namespace name="fco" file="../formcomponents.mako"/>

<div class="alert alsert-error">
 アセット作成します。良いですか？
</div>

<div class="row">
  <div class="span5">
	${fco.form_to_table(form)}
  </div>

  <form action="${request.route_path("asset_create",asset_type=form.type)}" method="post">
    <button class="btn btn-primary" type="submit"><i class="icon-trash"> </i> Create</button>
    % for k,v in request.GET.iteritems():
      ${h.base.hidden_input(k,v)|n}
    % endfor
  </form>
</div>
