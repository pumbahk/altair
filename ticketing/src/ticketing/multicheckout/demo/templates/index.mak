<html>
  <head>
    <script type="text/javascript" src="/fanstatic/jquery/jquery.js"></script>
    <script type="text/javascript">
      $(function() {
        $('select[name="API"]').change(function(e){
          $('input[name!="order_no"], select[name!="API"]').attr('disabled', 'disabled');

          var api = $(this).val();
          if (api == 'secure3d_enrol') {
            $('input[name!="secure_code"], select').removeAttr('disabled');
          }
          if (api == 'checkout_auth_secure_code') {
            $('input, select').removeAttr('disabled');
          }
          if (api == 'checkout_sales_part_cancel') {
            $('input[name="total_amount"]').removeAttr('disabled');
          }
        }).change();
      });
    </script>
  </head>
  <body>
  <form ${request.route_url('top')} method="post">
    <ul>
      <li>
        <label>API</label>
        <select name="API">
          <option value="secure3d_enrol">3D認証可否確認〜3D認証結果取得〜オーソリ(3D)</option>
          <option value="checkout_auth_secure_code">オーソリ(セキュアコード)</option>
          <option value="checkout_auth_cancel">オーソリ取消</option>
          <option value="checkout_sales_secure3d">売上(3D)</option>
          <option value="checkout_sales_secure_code">売上(セキュアコード)</option>
          <option value="checkout_sales_cancel">売上取消</option>
          <option value="checkout_sales_part_cancel">売上一部キャンセル</option>
          <option value="checkout_inquiry">取引照会</option>
        </select>
      </li>
      <li>
        <label>order_no</label>
        <input type="text" name="order_no" value="${order_no}" />
      </li>
      <li>
        <label>client_name</label>
        <input name="client_name" value="テスト" />
      </li>
      <li>
        <label>card_number</label>
        <input name="card_number" />
      </li>
      <li>
        <label>card_holder_name</label>
        <input name="card_holder_name" value="TEST" />
      </li>
      <li>
        <label>mail_address</label>
        <input name="mail_address" />
      </li>
      <li>
        <label>exp_month</label>
        <select name="exp_month">
          <option value="01">1</option>
          <option value="02">2</option>
          <option value="03">3</option>
          <option value="04">4</option>
          <option value="05">5</option>
          <option value="06">6</option>
          <option value="07">7</option>
          <option value="08">8</option>
          <option value="09">9</option>
          <option value="10">10</option>
          <option value="11">11</option>
          <option value="12">12</option>
        </select>
      </li>
      <li>
        <label>exp_year</label>
        <select name="exp_year">
          <option value="12">2012</option>
          <option value="13">2013</option>
          <option value="14">2014</option>
          <option value="15">2015</option>
          <option value="16">2016</option>
          <option value="17">2017</option>
          <option value="18">2018</option>
          <option value="19">2019</option>
          <option value="20">2020</option>
        </select>
      </li>
      <li>
        <label>total_amount</label>
        <input type="text" value="10" name="total_amount" />
      </li>
      <li>
        <label>secure_code</label>
        <input type="text" name="secure_code" />
      </li>
    </ul>
    <button type="submit">Submit</button>
  </form>
  </body>
</html>