<%inherit file="altaircms:templates/front/simple/col2.mako"/>
<%def name="widgets(name)">
  % for w in display_blocks[name]:
      ${w|n}
  % endfor
</%def>

<%block name="header">${self.inherits.header()} ${widgets("header")}</%block>
<%block name="left">${self.inherits.left()} ${widgets("left")}</%block>
<%block name="right">${self.inherits.right()} ${widgets("right")}</%block>
<%block name="footer">${self.inherits.footer()} ${widgets("footer")}</%block>

<%block name="css_prerender">${self.inherits.css_prerender()} ${widgets("css_prerender")}</%block>
<%block name="js_prerender">${self.inherits.js_prerender()} ${widgets("js_prerender")}</%block>
<%block name="js_postrender">${self.inherits.js_postrender()} ${widgets("js_postrender")}</%block>

