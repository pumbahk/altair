<%! import markupsafe %>
<%def name="list(items, container_classes=[], item_classes=[])">
<%
container_classes = isinstance(container_classes, basestring) and container_classes.split(u' ') or container_classes
item_classes = isinstance(item_classes, basestring) and item_classes.split(u' ') or item_classes
%>
<ul${(container_classes and u' class="%s"' % markupsafe.escape(u' '.join(container_classes)) or u'')|n}>
% for i, item in enumerate(items):
  <%
  _item_classes = item_classes and list(item_classes) or []
  if i == 0: _item_classes.append('first')
  %>
  <li${(_item_classes and u' class="%s"' % markupsafe.escape(u' '.join(_item_classes)) or u'')|n}>${caller.body(i, item)}</li>
% endfor
</ul>
</%def>
