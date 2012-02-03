<%namespace name="self" file="list.mako" />
<%! from ticketing.resources import ActingAsBreadcrumb %>
% if ActingAsBreadcrumb.providedBy(request.context):
<%
breadcrumb_list = []
def helper(context):
  if context is not None:
    assert ActingAsBreadcrumb.providedBy(context)
    breadcrumb_list.append(context)
    helper(context.navigation_parent)
helper(request.context)
breadcrumb_list.reverse()
%>
<%self:list container_classes="breadcrumb" items="${breadcrumb_list}" args="i, item">
% if i == len(breadcrumb_list) - 1:
  ${item.navigation_name}
% else:
  <a href="${request.resource_url(item)}">${item.navigation_name}</a>
% endif
</%self:list>
% endif
