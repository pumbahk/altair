## promotion widget dialog
##  view function is views.PromotionWidgetView.dialog
##
<%namespace file="../components.mako" name="co"/>

<div class="title">
  <h1>プロモーション枠　widget</h1>
</div>

<table class="table">
  <tbody>
    ${co.formfield(form, "kind")}
    ${co.formfield(form, "promotion")}
  </tbody>
</table>
<button type="button" id="promotion_submit">登録</button>
