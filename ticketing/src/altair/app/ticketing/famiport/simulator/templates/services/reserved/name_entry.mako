<%inherit file="/_base.mako" />
<h1>申込者氏名入力画面</h1>
<div>
  <form action="${request.current_route_path()}" method="POST">
    <fieldset>
      <input type="text" name="customer_name" placeholder="申込者氏名" value="${customer_name}" />
      <input type="submit" class="btn" />
    </fieldset>
  </form>
</div>

