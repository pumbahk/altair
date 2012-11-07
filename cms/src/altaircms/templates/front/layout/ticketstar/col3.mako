<%inherit file="altaircms:templates/front/simple/col3.mako"/>
<%def name="widgets(name)">
  % for w in display_blocks[name]:
      ${w|n}
  % endfor
</%def>

<%block name="header">${self.inherits.header()} ${widgets("header")}</%block>
<%block name="left1">${self.inherits.left1()} ${widgets("left1")}</%block>
<%block name="right1">${self.inherits.right1()} ${widgets("right1")}</%block>
<%block name="left2">${self.inherits.left2()} ${widgets("left2")}</%block>
<%block name="center">${self.inherits.center()} ${widgets("center")}</%block>
<%block name="right2">${self.inherits.right2()} ${widgets("right2")}</%block>
<%block name="footer">${self.inherits.footer()} ${widgets("footer")}</%block>

<%block name="css_prerender">${self.inherits.css_prerender()} ${widgets("css_prerender")}</%block>
<%block name="js_prerender">${self.inherits.js_prerender()} ${widgets("js_prerender")}</%block>
<%block name="js_postrender">${self.inherits.js_postrender()} ${widgets("js_postrender")}</%block>

