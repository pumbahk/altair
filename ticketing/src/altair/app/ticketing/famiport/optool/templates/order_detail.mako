<!DOCTYPE html>
<html>

<%include file="header.mako"/>

<body>
  <div class="container">
    <%include file="menu.mako"/>

    <!-- Main component for a primary marketing message or call to action -->
    <div id="table-content">
      <h3>申込詳細</h3>
      <table class="table table-hover">
        <thead>
          <tr>
            <th colspan="4">申込情報</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <th>払込票番号</th>
            <td>aaaaaaaaa</td>
            <th>申込ステータス</th>
            <td>bbbbbbbbb</td>
          </tr>
          <tr>
            <th>引換票番号</th>
            <td></td>
            <th>発券区分</th>
            <td></td>
          </tr>
          <tr>
            <th>管理番号</th>
            <td></td>
            <th>受付日</th>
            <td></td>
          </tr>
          <tr>
            <th>氏名</th>
            <td></td>
            <th>氏名カナ</th>
            <td></td>
          </tr>
          <tr>
            <th>申込方法</th>
            <td></td>
            <th>電話番号</th>
            <td></td>
          </tr>
        </tbody>

        <thead>
          <tr>
            <th colspan="4">申込内容</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <th>興行コード</th>
            <td colspan="3">aaaaaaaaa</td>
          </tr>
          <tr>
            <th>公演名</th>
            <td colspan="3"></td>
          </tr>
          <tr>
            <th>会場</th>
            <td colspan="3"></td>
          </tr>
          <tr>
            <th>公演日時</th>
            <td colspan="3"></td>
          </tr>
          <tr>
            <th>申込サイト</th>
            <td colspan="3">cccccc</td>
          </tr>
          <tr>
            <th rowspan="2">席種・料金</th>
            <td rowspan="2">aaaa</td>
            <td colspan="2">aaaa</td>
          </tr>
          <tr>
            <td colspan="2">aaaa</td>
          </tr>
        </tbody>

        <thead><tr><th colspan="4"></th></tr></thead>
        <tbody>
          <tr>
            <th>料金合計</th>
            <td colspan="3">aaaaaaaaa</td>
          </tr>
          <tr>
            <th rowspan="3">内訳</th>
            <td colspan="1">チケット代金</td>
            <td colspan="2">333333</td>
          </tr>
          <tr>
            <td colspan="1">発券手数料</td>
            <td colspan="2">111</td>
          </tr>
          <tr>
            <td colspan="1">システム利用料</td>
            <td colspan="2">222</td>
          </tr>
          <tr>
            <th>レジ支払い金額</th>
            <td colspan="3">cccccc</td>
          </tr>
        </tbody>

        <thead><tr><th colspan="4"></th></tr></thead>
        <tbody>
          <tr>
            <th>Famiポート受付日時</th>
            <td>aaaaaaaaa</td>
            <th>発券日時</th>
            <td>aaaaaaaaa</td>
          </tr>
          <tr>
            <th>発券店番</th>
            <td>aaaaaaaaa</td>
            <th>発券店舗</th>
            <td>aaaaaaaaa</td>
          </tr>
          <tr>
            <th>バーコード番号1</th>
            <td colspan="3"></td>
          </tr>
          <tr>
            <th>バーコード番号2</th>
            <td colspan="3"></td>
          </tr>
          <tr>
            <th>バーコード番号3</th>
            <td colspan="3"></td>
          </tr>
          <tr>
            <th>備考</th>
            <td colspan="3"></td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="buttonBoxBottom pull-right">
      <a href="re_order.html"><button type="submit" class="btn btn-info">発券指示</button></a>
      <button type="submit" class="btn btn-info">発券取消</button>
    </div>
    <footer style="text-align:center;">
      <div>&copy; 2012 TicketStar Inc.</div>
      <div>version =</div>
    </footer>
  </div>
  <!-- /container -->
</body>

</html>
