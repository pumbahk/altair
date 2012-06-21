<%def name="index_search_form(request)">
  <form action="${request.route_path("mobile_search")}" class="searchbox"><font size="3">
	&#xe691;チケット検索<br />
	<input class="text_field" type="text" name="q" value="" /><input type="submit" value="検索" />
  </font>
  <table width="100%" cellspacing="1" cellpadding="2">
	<tbody>
	  <tr>
		<td bgcolor="#cccc88" width="50%" valign="center" align="center"><font size="1" color="#bf8000">&#xe67a;<a href="${request.route_path("mobile_category",category="music")}">音楽</a></font></td>
		<td bgcolor="#cccc88" width="50%" valign="center" align="center"><font size="1" color="#bf8000">&#xe653;<a href="${request.route_path("mobile_category",category="sports")}">スポーツ</a></font></td>
	  </tr>
	  <tr>
		<td bgcolor="#cccc88" valign="center" align="center"><font size="1" color="#bf8000">&#xe67c;<a href="${request.route_path("mobile_category",category="stage")}">演劇</a></font></td>
		<td bgcolor="#cccc88" valign="center" align="center"><font size="1" color="#bf8000">&#xe67d;<a href="${request.route_path("mobile_category",category="event")}">イベント・その他</a></font></td>
	  </tr>
	</tbody>
  </table>
  </form>
</%def>

<%def name="search_form(request)">
  <form action="${request.route_path("mobile_search")}" class="searchbox"><font size="3">
	&#xe691;チケット検索<br />
    <input type="hidden" name="r" value="${request.params.get("r","")}"/>
	<input class="text_field" type="text" name="q" value="" /><input type="submit" value="検索" />
  </font>
  </form>
</%def>
