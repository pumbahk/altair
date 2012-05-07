## heading widget dialog
##  view function is views.HeadingWidgetView.dialog
##
<%namespace file="../components.mako" name="co"/>

<div class="title">
  <h1>見出し　widget</h1>
</div>

<table class="table">
  <tbody>
    ${co.formfield(form, "kind")}
    ${co.formfield(form, "text")}
  </tbody>
</table>
<button type="button" id="submit">登録</button>
