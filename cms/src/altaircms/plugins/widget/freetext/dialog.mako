<script type="text/javascript" src="/static/js/jquery.cleditor.min.js"></script>


<div class="title">
  <h1>フリーテキスト</h1>
</div>

<div style="align:center">
  <textarea id ="freetext_widget_textarea">
	${widget.text or ""}
  </textarea>
</div>

<button class="btn" type="button" id="freetext_submit">フリーテキスト登録</button>
<br/>

<form class="well" style="margin-top:10px;">
  ${choice_form.default_text.label}
  <span class="help-block">保存した定型文を挿入することができます</span>
  ${choice_form.default_text}
  <button class="btn btn-small" type="button" id="freetext_default_body_submit">定型文挿入</button>	
  <a target="blank" href="${request.route_path("freetext_default_list")}">定型文登録</a>
</form>




