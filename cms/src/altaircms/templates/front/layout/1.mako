<%inherit file='altaircms:templates/front/ticket-rakuten-co-jp/layout.mako'/>
<%def name="widgets(name)">
  % for w in display_blocks[name]:
	  ${w|n}
  % endfor
</%def>
<%block name="header">
  ${widgets("header")}
</%block>
<%block name="content">
  ${widgets("content")}
</%block>
<%block name="footer">
  ${widgets("footer")}
</%block>
