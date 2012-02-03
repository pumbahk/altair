<%inherit file="../layout.mako" />
<%block name="title">ユーザ詳細</%block>
<div class="ui-toolbar">
  <a href="${request.route_path('admin.users.new')}" class="ui-button">編集</a>
  <a href="#" class="ui-button">削除</a>
</div>
<div class="subsection">
  <div class="subsection-header">
    <h2 class="subsection-header-content rounded">基本情報</h2>
  </div>
  <div class="subsection-main">
    <div class="subsection-main-content">
      <div class="twocolumns">
        <div class="first column">
          <div class="column-main">
            <div class="column-main-content">
              <table class="vertical-table fullwidth">
                <tbody>
                  <tr>
                    <th>ユーザID</th>
                    <td>1</td>
                  </tr>
                  <tr>
                    <th>ログインID</th>
                    <td>asdfasdf</td>
                  </tr>
                  <tr>
                    <th>氏名</th>
                    <td>松居 健太</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
        <div class="column">
          <div class="column-main">
            <div class="column-main-content">
              <table class="vertical-table fullwidth">
                <tbody>
                  <tr>
                    <th>ユーザ種別</th>
                    <td>クライアント</td>
                  </tr>
                  <tr>
                    <th>会社名</th>
                    <td>株式会社チケットスター</td>
                  </tr>
                  <tr>
                    <th>部署名</th>
                    <td>第一事業部</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
<div class="twocolumns">
  <div class="first column subsection">
    <div class="column-header subsection-header">
      <h2 class="column-header-content subsection-header-content rounded">連絡先</h2>
    </div>
    <div class="column-main subsection-main">
      <div class="column-main-content subsection-main-content">
        <table class="vertical-table fullwidth">
          <tbody>
            <tr>
              <th>郵便番号</th>
              <td>141-0022</td>
            </tr>
            <tr>
              <th>都道府県</th>
              <td>東京都</td>
            </tr>
            <tr>
              <th>市町村区以下の住所</th>
              <td>品川区東五反田5-21-15</td>
            </tr>
            <tr>
              <th>アパート・マンション名</th>
              <td>メタリオンOSビル 7F</td>
            </tr>
            <tr>
              <th>電話番号</th>
              <td>050-5830-6868</td>
            </tr>
            <tr>
              <th>携帯電話番号</th>
              <td>-</td>
            </tr>
            <tr>
              <th>FAX番号</th>
              <td>03-5795-1877</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
  <div class="column subsection">
    <div class="column-header subsection-header">
      <h2 class="column-header-content subsection-header-content rounded">振込先</h2>
    </div>
    <div class="column-main subsection-main">
      <div class="column-main-content subsection-main-content">
        <table class="vertical-table fullwidth">
          <tbody>
            <tr>
              <th>銀行名</th>
              <td>三菱東京UFJ銀行 (0005)</td>
            </tr>
            <tr>
              <th>銀行支店名</th>
              <td>あかね支店</td>
            </tr>
            <tr>
              <th>口座種別</th>
              <td>普通</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</div>
<div class="section">
  <div class="section-content">
    <div class="ui-tabs">
      <ul>
        <li><a href="#distributed_events">配券を受けているイベント</a></li>
        <li><a href="#distributing_events">配券しているイベント</a></li>
        <li><a href="#auctions">オークション</a></li>
      </ul>
      <div id="distributed_events" class="subsection">
        <div class="subsection-header">
          <div class="subsection-header-content">
            <h2>配券を受けているイベント</h2>
          </div>
          <div class="subsection-main">
            <div class="subsection-main-content">
              <%include file="../events/_list.mako" />
            </div>
          </div>
        </div>
      </div>
      <div id="distributing_events" class="subsection">
        <div class="subsection-header">
          <div class="subsection-header-content">
            <h2>配券しているイベント</h2>
          </div>
          <div class="subsection-main">
            <div class="subsection-main-content">
              <%include file="../events/_list.mako" />
            </div>
          </div>
        </div>
      </div>
      <div id="auctions" class="subsection">
        <div class="subsection-header">
          <div class="subsection-header-content">
            <h2>出品中のオークション</h2>
          </div>
          <div class="subsection-main">
            <div class="subsection-main-content">
              <form class="form">
                <table class="table fullwidth">
                  <thead>
                    <tr>
                      <th>-</th>
                      <th>ID</th>
                      <th>公演</th>
                      <th>開始〜終了日時</th>
                      <th>出品ユーザ</th>
                      <th>ステータス</th>
                      <th>現在価格 (入札者)</th>
                      <th>入札数</th>
                      <th>開始価格</th>
                      <th>席種名</th>
                      <th>券種名</th>
                      <th>ゲート / 列 / 座席番号</th>
                      <th>アイコン</th>
                      <th>アクション</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td rowspan="2"><input type="checkbox"></td>
                      <td rowspan="2">1</td>
                      <td rowspan="2">
                        公演1<br />
                        町田市民ホール 2011/12/4 18:00〜
                      </td>
                      <td rowspan="2">2011/11/3 10:00〜<br />2011/11/30 23:59</td>
                      <td rowspan="2"><a href="${request.route_path('admin.users.show', user_id=1)}">asdfasdf</a></td>
                      <td rowspan="2">受付中</td>
                      <td rowspan="2">\4,300 (<a href="${request.route_path('admin.users.show', user_id=2)}">fghjfghj</a>)</td>
                      <td>5</td>
                      <td rowspan="2">\4,000</td>
                      <td>A席</td>
                      <td>A席大人</td>
                      <td>A / R / 5</td>
                      <td rowspan="2">
                        <span class="seat-icon-consecutive"></span>
                        <span class="seat-icon-front_row"></span>
                        <span class="seat-icon-isle_side"></span>
                      </td>
                      <td rowspan="2">
                        <a href="${request.route_path('admin.auction.show', auction_id=1)}">詳細</a>
                      </td>
                    </tr>
                    <tr>
                      <td>A席</td>
                      <td>A席大人</td>
                      <td>A / R / 6</td>
                    </tr>
                    <tr>
                      <td rowspan="2"><input type="checkbox"></td>
                      <td>2</td>
                      <td>
                        公演2<br />
                        なかのZEROホール 2012/2/1 16:00〜
                      </td>
                      <td>2012/1/5 10:00〜<br />2012/1/24 23:59</td>
                      <td><a href="${request.route_path('admin.users.show', user_id=1)}">asdfasdf</a></td>
                      <td>イベント中止</td>
                      <td>- (-)</td>
                      <td>-</td>
                      <td>\2,000</td>
                      <td>S席</td>
                      <td>S席大人</td>
                      <td>- / 12 / 1</td>
                      <td>
                        <span class="seat-icon-premier"></span>
                        <span class="seat-icon-corner"></span>
                      </td>
                      <td>
                        <a href="${request.route_path('admin.auction.show', auction_id=2)}">詳細</a>
                      </td>
                    </tr>
                  </tbody>
                </table>
                </form>

                <h2>入札中のオークション</h2>
                <form class="form">
                <table class="table">
                  <thead>
                    <tr>
                      <th>-</th>
                      <th>ID</th>
                      <th>公演</th>
                      <th>開始〜終了日時</th>
                      <th>出品ユーザ</th>
                      <th>ステータス</th>
                      <th>現在価格 (入札者)</th>
                      <th>入札数</th>
                      <th>開始価格</th>
                      <th>席種名</th>
                      <th>券種名</th>
                      <th>ゲート / 列 / 座席番号</th>
                      <th>アイコン</th>
                      <th>アクション</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td rowspan="2"><input type="checkbox"></td>
                      <td rowspan="2">1</td>
                      <td rowspan="2">
                        公演1<br />
                        町田市民ホール 2011/12/4 18:00〜
                      </td>
                      <td rowspan="2">2011/11/3 10:00〜<br />2011/11/30 23:59</td>
                      <td rowspan="2"><a href="${request.route_path('admin.users.show', user_id=1)}">asdfasdf</a></td>
                      <td rowspan="2">受付中</td>
                      <td rowspan="2">\4,300 (<a href="${request.route_path('admin.users.show', user_id=2)}">fghjfghj</a>)</td>
                      <td>5</td>
                      <td rowspan="2">\4,000</td>
                      <td>A席</td>
                      <td>A席大人</td>
                      <td>A / R / 5</td>
                      <td rowspan="2">
                        <span class="seat-icon-consecutive"></span>
                        <span class="seat-icon-front_row"></span>
                        <span class="seat-icon-isle_side"></span>
                      </td>
                      <td rowspan="2">
                        <a href="${request.route_path('admin.auction.show', auction_id=1)}">詳細</a>
                      </td>
                    </tr>
                    <tr>
                      <td>A席</td>
                      <td>A席大人</td>
                      <td>A / R / 6</td>
                    </tr>
                    <tr>
                      <td rowspan="2"><input type="checkbox"></td>
                      <td>2</td>
                      <td>
                        公演2<br />
                        なかのZEROホール 2012/2/1 16:00〜
                      </td>
                      <td>2012/1/5 10:00〜<br />2012/1/24 23:59</td>
                      <td><a href="${request.route_path('admin.users.show', user_id=1)}">asdfasdf</a></td>
                      <td>イベント中止</td>
                      <td>- (-)</td>
                      <td>-</td>
                      <td>\2,000</td>
                      <td>S席</td>
                      <td>S席大人</td>
                      <td>- / 12 / 1</td>
                      <td>
                        <span class="seat-icon-premier"></span>
                        <span class="seat-icon-corner"></span>
                      </td>
                      <td>
                        <a href="${request.route_path('admin.auction.show', auction_id=2)}">詳細</a>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
