## linklist widget dialog
##  view function is views.LinklistWidgetView.dialog
##
<%namespace file="../components.mako" name="co"/>

<div class="title">
  <h1>リンクリスト　widget</h1>
</div>

<table class="table">
  <tbody>
    ${co.formfield(form, "finder_kind")}
    ${co.formfield(form, "max_items")}
    ${co.formfield(form, "delimiter")}
  </tbody>
</table>
<button type="button" id="linklist_submit">登録</button>
