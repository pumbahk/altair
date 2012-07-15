## rawhtml widget dialog
##  view function is views.RawhtmlWidgetView.dialog
##
<div class="title">
  <h1>rawHTML</h1>
</div>
 <p class="lead">ここに登録したHTMLがそのままレンダリングされます。ご利用は計画的に</p>

<textarea id ="rawhtml_body">
${widget.text or ""}
</textarea>
<hr/>
<button type="button" id="rawhtml_submit">登録</button>
