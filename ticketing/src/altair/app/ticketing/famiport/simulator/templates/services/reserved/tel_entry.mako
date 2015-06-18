<%inherit file="/_base.mako" />
<h1>申込者電話番号入力画面</h1>
<div>
  <form action="${request.current_route_path()}" method="POST">
    <fieldset>
      <input type="text" name="customer_phone_number" placeholder="申込者電話番号" value="${customer_phone_number}" />
      <input type="submit" class="btn" />
    </fieldset>
  </form>
</div>


