<form>
  <div class="ui-toolbar">
    <a href="${request.route_path('admin.manager.new')}" class="ui-button">新規ユーザ</a>
    <a href="${request.route_path('admin.manager.edit_multiple')}" class="ui-button">まとめて編集</a>
    <a href="#" class="ui-button">まとめて削除</a>
  </div>
  <table class="table fullwidth checkboxed_table">
    <thead>
      <tr>
        <th class="minwidth"><input type="checkbox" class="__action__-select_all" /></td>
        <th class="minwidth">ID</th>
        <th>ログインID</th>
        <th>ユーザ種別</th>
        <th>会社名</th>
        <th>部署名</th>
        <th>氏名</th>
        <th>郵便番号</th>
        <th>都道府県</th>
        <th>市町村区以下の住所</th>
        <th>アパート・マンション名</th>
        <th>電話番号</th>
        <th>携帯電話番号</th>
        <th>FAX番号</th>
        <th>銀行名</th>
        <th>銀行支店名</th>
        <th>口座種別</th>
        <th>口座番号</th>
      </tr>
    </thead>
    <tbody>
    % for manager in managers:
      <tr>
        <td><input type="checkbox" /></td>
        <td><a href="${request.route_path('admin.manager.show', user_id=1)}">1</a></td>
        <td><a href="${request.route_path('admin.manager.show', user_id=1)}">asdfasdf</a></td>
        <td>クライアント</td>
        <td>株式会社チケットスター</td>
        <td>第一事業部</td>
        <td>松居 健太</td>
        <td>141-0022</td>
        <td>東京都</td>
        <td>品川区東五反田5-21-15</td>
        <td>メタリオンOSビル 7F</td>
        <td>050-5830-6868</td>
        <td>-</td>
        <td>03-5795-1877</td>
        <td>三菱東京UFJ銀行</td>
        <td>あかね支店</td>
        <td>普通</td>
        <td>0000000</td>
      </tr>
    % endfor
    </tbody>
  </table>
</form>
