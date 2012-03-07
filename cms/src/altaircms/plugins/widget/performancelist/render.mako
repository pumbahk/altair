## performancelist widget output template
## 

<div class="performances">
    <form>
      <div class="fields">
        <div class="field">
          <input type="checkbox" id="form-showUnavailablePerformances"><label for="form-showUnavailablePerformances">販売終了した公演も表示</label>
        </div>
      </div>
    </form>
    <table>
      <thead>
        <tr>
          <th class="serial">&nbsp;</th>
          <th class="performance_name">公演名</th>
          <th class="performance_period">公演日時</th>
          <th class="venue">会場</th>
          <th class="action">&nbsp;</th>
        </tr>
      </thead>
      <tbody>
      % for p in performances:
        ## あとで修正
        <tr id="performance-${p.id}">
		  <td class="serial">
            <span class="serial">${p.id}</span>
          </td>
          <td class="performance_name">
             ${ p.title }
          </td>
          <td class="performance_period">
            ## たぶん期間が存在するとき分岐する(helperで指定するようにする)
            <span class="date">${p.open_on.year}年${ p.open_on.month }月${p.open_on.day }日(${ WEEK[p.open_on.weekday()] }) ${ p.open_on.hour }:00</span>
          </td>
          <td class="venue">
             ${ p.venue }
          </td>
          <td class="action">
            <a href="https://www.e-get.jp/tstar/pt/&amp;s=SCMNF0603" class="button reserve_or_order button-reserve_or_order">予約・購入(未実装)</a>
          </td>
        </tr>
      % endfor
      </tbody>
    </table>
</div>
