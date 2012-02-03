<div class="form-fieldseq ${field.widget.css_class or ''}" id="${field.oid}">
<%
rndr = field.renderer
item_tmpl = field.widget.item_template
min_len   = field.widget.min_len or 0
max_len   = field.widget.max_len or 100000
now_len   = len(subfields)
prototype = field.widget.prototype(field)
%>
  <!-- sequence -->
  <input type="hidden" name="__start__" value="${field.name}:sequence" class="deformProto" prototype="${prototype|n}" />
  <div class="form-fieldseq-fields">
    % if getattr(field.widget, 'list_item_field_names', False):
    <div class="form-fieldseq-fieldnames">
      % for item_field in field.children[0].children:
      <div class="form-fieldseq-fieldname">${item_field.title}</div>
      % endfor
    </div>
    % endif
    % for cstruct, _field in subfields:
      ${rndr(item_tmpl, field=_field, cstruct=cstruct, parent=field)|n}
    % endfor
    <span class="deformInsertBefore" min_len="${min_len}" max_len="${max_len}" now_len="${now_len}"></span>
  </div>
  
  <a href="#" class="deformSeqAdd" id="${field.oid}-seqAdd"
     onclick="javascript: return deform.appendSequenceItem(this);">
    <span id="${field.oid}-addtext">${add_subitem_text.interpolate()}</span>
  </a>

  <script type="text/javascript">
     deform.addCallback(
       '${field.oid}',
       function(oid) {
         oid_node = $('#'+ oid);
         deform.processSequenceButtons(oid_node, ${min_len}, 
                                       ${max_len}, ${now_len});
       }
     )
  </script>

  <input type="hidden" name="__end__" value="${field.name}:sequence"/>

  <!-- /sequence -->

</div>
