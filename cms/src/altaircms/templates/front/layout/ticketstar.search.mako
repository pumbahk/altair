<%inherit file="altaircms:templates/front/ticketstar/search/detail_search_result.mako"/>
<%namespace file="altaircms:templates/front/ticketstar/gadgets.mako" name="gadgets"/>

<%block name="main">

	  <h3>検索条件:</h3>
      <div id="searchQuery">
		## 検索条件指定(intersection,union)？
		${query_params}
	  </div>
	<h2><img src="/static/ticketstar/img/search/title_results.gif" alt="チケット検索結果" width="742" height="43" /></h2>
	% if not result_seq:
	  <div class="search-message">
		<h3>該当するチケットはありません</h3>
		<p class="message">他の検索条件で再度検索してみてください</p>
		${gadgets.search_form_on_header(u"アーティスト名、公演名、会場名など")}
	  </div>
	% endif

	% for result in result_seq:
	  ${result}
	% endfor
</%block>
