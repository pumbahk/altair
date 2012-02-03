<%
nooutertag = getattr(field.widget, 'nooutertag', False)
if getattr(field.widget, 'nofieldset', False):
  fieldset = 'div'
  legend = 'div'
else:
  fieldset = 'fieldset'
  legend = 'legend'
%>
% if not nooutertag:
<div class="form-subform">
  <${fieldset} class="deformMappingFieldset form-subform-fields">
    <!-- mapping -->
    % if field.title and not getattr(field.widget, 'notitle', False):
    <${legend} class="form-subform-title">${field.title}</${legend}>
    % endif
    % if field.description and not getattr(field.widget, 'nodescription', False):
    <div class="form-subform-description">
      <p>${field.description}</p>
    </div>
    % endif
    % if field.errormsg:
    <div class="form-subform-errors">
      <p>There was a problem with this section</p>
      <p class="errorMsg">${field.errormsg}</p>
    </div>
    % endif
% endif
    <input type="hidden" name="__start__" value="${field.name}:mapping"/>
    % for f in field.children:
    <%
       rndr = field.renderer
       tmpl = field.widget.item_template
    %>
      ${rndr(tmpl,field=f,cstruct=cstruct.get(f.name,null))|n}
    % endfor
    <input type="hidden" name="__end__" value="${field.name}:mapping"/>
    <!-- /mapping -->
% if not nooutertag:
  </${fieldset}>
</div>
% endif 
