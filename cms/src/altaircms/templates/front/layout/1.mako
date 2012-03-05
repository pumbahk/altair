<%inherit file='altaircms:templates/front/ticket-rakuten-co-jp/layout.mako'/>
<%def name="widgets(name)">
  % for w in display_blocks[name]:
	  ${w|n}
  % endfor
</%def>

<%block name="fulltitle">${self.inherits.fulltitle()} ${widgets("fulltitle")}</%block>
<%block name="description">${self.inherits.description()} ${widgets("description")}</%block>
<%block name="keyword">${self.inherits.keyword()} ${widgets("keyword")}</%block>
<%block name="js_prerender">${self.inherits.js_prerender()} ${widgets("js_prerender")}</%block>
<%block name="js_postrender">${self.inherits.js_postrender()} ${widgets("js_postrender")}</%block>
<%block name="style">${self.inherits.style()} ${widgets("style")}</%block>
<%block name="page">${self.inherits.page()} ${widgets("page")}</%block>
<%block name="content">${self.inherits.content()} ${widgets("content")}</%block>
<%block name="footer">${self.inherits.footer()} ${widgets("footer")}</%block>
<%block name="js_foot">${self.inherits.js_foot()} ${widgets("js_foot")}</%block>
