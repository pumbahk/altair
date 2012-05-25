<%inherit file="altaircms:templates/front/ticketstar/search/detail_search_input.mako"/>
<%namespace file="altaircms:templates/front/ticketstar/gadgets.mako" name="gadgets"/>

<%block name="main">
		<!-- InstanceBeginEditable name="main" -->
		<form action="${request.route_path("page_search_result")}" method="GET">
		<div class="searchInput">
		  <dl>
			<dt><div class="searchInputHeader">フリーワードで探す</div></dt>
			<dd>
			  ${forms.query}
			</dd>
		  </dl>
		</div>

		<div class="searchInput">
		  <dl>
			<dt><div class="searchInputHeader">ジャンルで探す</div></dt>
			<dd>
			  <table>
				  <tbody>
					${forms.genre}
				  </tbody>
				</table>
			</dd>
		  </dl>
		</div>

		<div class="searchInput">
		  <dl>
			<dt><div class="searchInputHeader">開催地で探す</div></dt>
			<dd>
			  <table>
				  <tbody>
					${forms.area}
				  </tbody>
			  </table>
			</dd>
		  </dl>
		</div>

		<div class="searchInput">
		  <dl>
			<dt><div class="searchInputHeader">公演日で探す</div></dt>
			<dd>
			  ${ forms.performance_term }
			</dd>
		  </dl>
		</div>
		
		<div class="searchInput">
		  <dl>
			<dt><div class="searchInputHeader">販売条件</div></dt>
			<dd>
			  ${ forms.deal_cond }
			</dd>
		  </dl>
		</div>

		<div class="searchInput">
		  <dl>
			<dt><div class="searchInputHeader">付加サービス</div></dt>
			<dd>
			  ${ forms.added_service }
			</dd>
		  </dl>
		</div>

		<div class="searchInput">
		  <dl>
			<dt><div class="searchInputHeader">発売日</div></dt>
			<dd>
			  ${ forms.about_deal }
			</dd>
		  </dl>
		</div>

		<div id="searchFormButton">
		  <ul>
			<li>
			  <a href="${request.route_path("page_search_input")}"><img src="/static/ticketstar/img/search/btn_clear.gif" alt="条件をクリア" name="clear_button"/></a>
			</li>
			<li><input type="image" src="/static/ticketstar/img/search/btn_search.gif" alt="検索" name="search_button"/></li>
		  </ul>
		</div>
	</form>
</%block>

<%block name="side">
    ${gadgets.sidebar_category_listing(categories)}

	<dl id="sideRefineSearch">
		${gadgets.sidebar_area_listing(areas)}
		${gadgets.sidebar_deal_cond_listing()}
		${gadgets.sidebar_deal_open_listing()}
		${gadgets.sidebar_event_open_listing()}
	</dl>

	${gadgets.sidebar_maintenance()}
	<!-- InstanceEndEditable -->
	${gadgets.sidebar_sideBtn()}
</%block>


