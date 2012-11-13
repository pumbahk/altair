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
	  <div class="searchMessage">
		<h3>該当するチケットはありません</h3>
		<p class="message">他の検索条件で再度検索してみてください</p>
		${gadgets.search_form_on_header(u"アーティスト名、公演名、会場名など", "missing_query_id")}
	  </div>
	% else:

	  <%
seq = h.paginate(request, result_seq, items_per_page=10, item_count=len(result_seq))
current_items_count = seq.page * seq.items_per_page
%>
	  <div id="paginateInfo">
		<p class="align1">
		  全 ${seq.item_count }件中
		  ${max(1,current_items_count - seq.items_per_page)}〜${min(current_items_count,seq.item_count)}件を表示中
		</p>
	  </div>

	  ${seq.pager(format=u"$link_first $link_previous 前を表示 ~3~ 次を表示 $link_next $link_last ")}

	  % for result in seq.paginated():
		${result}
	  % endfor

	  ${seq.pager(format=u"$link_first $link_previous 前を表示 ~3~ 次を表示 $link_next $link_last ")}
    % endif
</%block>

<%block name="side">
  <!-- InstanceBeginEditable name="side" -->
    ${gadgets.sidebar_category_listing(categories)}

	<dl id="sideRefineSearch">
		${gadgets.sidebar_area_listing(areas)}
		${gadgets.sidebar_deal_cond_listing()}
		${gadgets.sidebar_deal_open_listing()}
		${gadgets.sidebar_event_open_listing()}
	</dl>

##	${gadgets.sidebar_maintenance()}
	<!-- InstanceEndEditable -->
##	${gadgets.sidebar_sideBtn()}
</%block>
