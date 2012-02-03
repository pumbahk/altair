<input type="text" name="${field.name}" value="${cstruct}" ${field.widget.size and 'size="%d"' % field.widget.size or ''} class="datetime-field ${field.widget.css_class or ''}" id="${field.oid}"/>
<script type="text/javascript">
  deform.addCallback(
    '${field.oid}',
    function(oid) {
        $('#' + oid).datetimepicker(${options|n});
    }
  );
</script>
