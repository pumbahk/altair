<%inherit file='altaircms:front/tests/templates/base.mako'/>
<%def name="widgets(name)">
  % for w in display_blocks[name]:
	  ${w|n}
  % endfor
</%def>
<%block name="page">${self.inherits.page()} ${widgets("page")}</%block>
<%block name="js_prerender">${self.inherits.js_prerender()} ${widgets("js_prerender")}</%block>
<%block name="js_postrender">${self.inherits.js_postrender()} ${widgets("js_postrender")}</%block>
<%block name="header">${self.inherits.header()} ${widgets("header")}</%block>
<%block name="content">${self.inherits.content()} ${widgets("content")}</%block>
<%block name="footer">${self.inherits.footer()} ${widgets("footer")}</%block>
