<form class="form ${field.widget.css_class or ''}" id="${field.formid}" action="${field.action}" method="${field.method}" enctype="multipart/form-data" accept-charset="utf-8">
  <input type="hidden" name="_charset_" />
  <input type="hidden" name="__formid__" value="${field.formid}"/>
  <div class="form-header">
    % if field.title:
    <h3 class="form-title">${field.title}</h3>
    % endif
    % if field.description:
    <div class="form-description">
      <p>${field.description}</p>
    </div>
    % endif
    % if field.error: 
    <div class="form-errors">
      <p>There was a problem with your submission</p>
      <p>Errors have been highlighted below</p>
    </div>
    % endif
  </div>
  <div class="form-fields">
    <%
       rndr = field.renderer
       tmpl = field.widget.item_template
    %>
    % for f in field.children:
      ${rndr(tmpl, field=f, cstruct=cstruct.get(f.name, null))|n}
    % endfor 
  </div>
  <div class="form-footer">
    % for button in field.buttons:
    <button ${button.disabled and 'disabled="disabled"' or ''|n} id="${field.formid+button.name}" name="${button.name}" type="${button.type}" class="submit" value="${button.value}">
      <span>${button.title}</span>
    </button>
    % endfor
  </div>
  % if field.use_ajax:
  <script type="text/javascript">
  function deform_ajaxify(response, status, xhr, form, oid, mthd){
     var options = {
       target: '#' + oid,
       replaceTarget: true,
       success: function(response, status, xhr, form){
         deform_ajaxify(response, status, xhr, form, oid);
       }
     };
     var extra_options = ${field.ajax_options};
     var name;
     if (extra_options) {
       for (name in extra_options) {
         options[name] = extra_options[name];
       };
     };
     $('#' + oid).ajaxForm(options);
     if(mthd){
       mthd(response, status, xhr, form);
     }
  }
  deform.addCallback(
     '${field.formid}',
     function(oid) {
       deform_ajaxify(null, null, null, null, oid);
     }
  );
  </script>
  % endif
</form>
