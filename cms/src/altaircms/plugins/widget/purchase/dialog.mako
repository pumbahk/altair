## purchase widget dialog
##  view function is views.PurchaseWidgetView.dialog
##
<%namespace file="../components.mako" name="co"/>

<div class="title">
  <h1>購入ボタン　widget</h1>
</div>

<table class="table">
  <tbody>
    ${co.formfield(form, "kind")}
    ${co.formfield(form, "external_link")}
  </tbody>
</table>
<button type="button" id="submit">登録</button>
