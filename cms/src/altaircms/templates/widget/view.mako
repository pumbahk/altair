<%inherit file='../layout.mako'/>

${widget}


<form action="${request.route_url('widget', widget_id=widget.id)}" method="post">
${form}
  <input type="hidden" name="_method" value="delete">
  <button type="submit">削除</button>
</form>
