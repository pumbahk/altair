## gadgets ＝ ある程度まとまったhtmlの構成要素。

## ヘッダーの検索フォーム.jsと連携している
<%def name="search_form_on_header(placeholder)">
	<form id="form1" name="form1" method="GET" action="${request.route_path("page_search_by",kind="freeword")}">
		<input name="textfield" type="text" id="textfield" size="40" value="${placeholder}" onblur="if(this.value=='') this.value='${placeholder}';" onfocus="if(this.value=='${placeholder}') this.value='';" />
		<input name="imageField" type="image" id="imageField" src="/static/ticketstar/img/common/header_search_btn.gif" alt="検索" />
		<a href="${request.route_path("page_search_input")}">詳細検索</a>
	</form>
</%def>


