## detail widget dialog
##  view function is views.DetailWidgetView.dialog
##
<div class="title">
  <h1>イベント詳細</h1>
</div>

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
<button type="button" id="detail_submit">登録</button>

