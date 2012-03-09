## detail widget dialog
##  view function is views.DetailWidgetView.dialog
##
<div id="select_detail">
%for field in form:
  <tr>
    %if field.type == "BooleanField":
      <td></td>
      <td>${field} ${field.label}</td>
    %else:
      <td>${ field.label }</td>
      <td>${ field }
    %endif
  </tr>
%endfor
</div>
<hr/>
<button type="button" id="submit">登録</button>

