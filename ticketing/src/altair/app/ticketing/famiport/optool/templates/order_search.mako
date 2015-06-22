<%inherit file="_base.mako"/>

<div class="jumbotron">
  <form class="form">
    <div class="row">
      <div class="col-md-10">
        <h3 class="form-heading">申込検索</h3>
        <table class="search-table">
          <tbody>
            <tr>
              <th>
                <label class="pull-right">払込票番号：</label>
              </th>
              <td>
                <input type="text" name="payment_num" class="form-control" autofocus>
              </td>
              <th>
                <label class="pull-right">引換票番号：</label>
              </th>
              <td>
                <input type="text" name="hikikae_num" class="form-control">
              </td>
            </tr>
            <tr>
              <th>
                <label class="pull-right">管理番号：</label>
              </th>
              <td>
                <input type="text" name="control_num" class="form-control">
              </td>
              <th>
                <label class="pull-right">バーコード番号：</label>
              </th>
              <td>
                <input type="text" name="barcode" class="form-control">
              </td>
            </tr>
            <tr>
              <th>
                <label class="pull-right">電話番号：</label>
              </th>
              <td>
                <input type="text" name="tel" class="form-control">
              </td>
              <th>
                <label class="pull-right">店番：</label>
              </th>
              <td>
                <input type="text" name="store_num" class="form-control">
              </td>
            </tr>
          </table>
      </div>
      <div class="col-md-2 buttonBox">
        <button type="submit" class="btn btn-default">Clear<span class="glyphicon glyphicon-erase"></span></button>
        <button type="submit" class="btn btn-lg btn-default">Search
          <span class="glyphicon glyphicon-search"></span>
        </button>
      </div>
    </div>
  </form>
</div>
<div id="table-content">
  <div class="row">
    <div class="col-md-3 text-center">
      <h4>申込検索結果一覧</h4>
    </div>
    <div class="col-md-9 text-center">
      <h4>検索結果件数◯◯件</h4>
    </div>
  </div>
  <table class="table table-hover">
    <thead>
      <tr>
        <th>選択</th>
        <th>申込区分</th>
        <th>興行名</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><input type="radio" value="1" name="radio_gr" form="order"></td>
        <td>一般販売</td>
        <td>鹿島vs横浜（一般販売）</td>
      </tr>
      <tr>
        <td><input type="radio" value="2" name="radio_gr" form="order"></td>
        <td>先行抽選</td>
        <td>鹿島vs横浜（先行抽選）</td>
      </tr>
      <tr>
        <td><input type="radio" value="3" name="radio_gr" form="order"></td>
        <td>あああ</td>
        <td>いいい</td>
      </tr>
    </tbody>
  </table>
</div>
<div class="buttonBoxBottom pull-right">
  <form id="order">
  <a href="re_order.html"><button type="button" class="btn btn-info">発券指示</button></a>
  <button type="submit" class="btn btn-info">発券取消</button>
  <button type="submit" class="btn btn-info">CSVダウンロード</button>
  <a id="to_detail" href=""><button type="button" class="btn btn-info">申込詳細</button></a>
  </form>
</div>

  <script type="text/javascript">
    $(document).ready(function(){
      $("*[name=radio_gr]:radio").change(function(){
        switch ($(this).val()){
          case "1":
            $("#to_detail").attr("href","order_detail.html");
            break;
          case "2":
            $("#to_detail").attr("href","lots_detail.html");
            break;
          case "3":
            console.log("3");
            break;
        }
      });
    });
  </script>

