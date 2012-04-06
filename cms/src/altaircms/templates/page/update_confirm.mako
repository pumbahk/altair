<%inherit file='../layout_2col.mako'/>
<%namespace name="co" file="components.mako"/>

<div class="row" style="margin-bottom: 9px">
  <h2 class="span6">更新確認画面 ページのタイトル - ${page.title} (ID: ${page.id})</h2>
</div>

<div class="row">
  <div class="alert alert-info">
  データ更新
  </div>
  <div class="span5">
    ${co.page_difference(page, dict(params))}
  </div>
  <div class="span6">
    <form action="${h.page.to_update(request,page)}" method="POST">
      <input id="_method" name="_method" type="hidden" value="put" />
      ## POST data
      %for k,v in params:
        <input id="${k}" name="${k}" type="hidden" value="${v|n}"/>
      %endfor
      ${h.base.execute_stage()|n}
      <button type="submit" class="btn btn-info"><i class="icon-trash icon-white"></i> Update</button>
    </form>        
  </div>
</div>
