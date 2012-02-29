<head></head>
<script>
        $("#calendar_type").live("change", function(){
            var type = $(this).val();
            var url = "/api/widget/calendar/dialog/demo/@type@".replace("@type@", type);
            $("#canpas").load(url);
        });

</script>
## calendar widget dialog
##  view function is views.CalendarWidgetView.dialog
##

<div id="select_calendar">
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

<h3>選択されたカレンダーのイメージ</h3>

<div id="canpas">
  
</div>
