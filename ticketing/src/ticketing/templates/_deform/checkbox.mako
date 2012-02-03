<input type="checkbox"
       name="${field.name}" value="${field.widget.true_val}"
       id="${field.oid}"
       class="checkbox ${field.widget.css_class or ''}" 
       ${("checked" if cstruct == field.widget.true_val else "")}
                       class field.widget.css_class"/>
