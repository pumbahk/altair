<input type="text" name="${field.name}" value="${cstruct}" ${field.widget.size and 'size="%d"' % field.widget.size or ''} class="text-field ${field.widget.css_class or ''}" id="${field.oid}"/>
% if field.widget.mask:
<script type="text/javascript">
  deform.addCallback(
     '${field.oid}',
     function (oid) {
        $("#" + oid).mask("${field.widget.mask}", 
                          {placeholder:"${field.widget.mask_placeholder}"});
     });
</script>
% endif
