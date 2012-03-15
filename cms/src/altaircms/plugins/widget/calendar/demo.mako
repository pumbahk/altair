<!-- <p>select: ${calendar_type}</p> -->
<style type="text/css">
    ul.calendar-tabmenu {
        margin: 0;
        padding: 0;
        border-bottom: 2px #ddd solid;
    }
    ul.calendar-tabmenu li {
        float: left;
        margin: 0 0 0 5px;
        position: relative;
        bottom: -2px;
        list-style-type: none;
    }
    ul.calendar-tabmenu li.none {
        border-bottom: 2px #fff solid;
        font-weight: bold;
    }
    ul.calendar-tabmenu li a {
        display: block;
        padding: 3px 10px 5px;
        text-decoration: none;
    }
/*
	ul.calendar-tabmenu li a.selected{
    	background-color:#333; /* todo remove it*/
        border-bottom: 2px #dd1d25 solid;
	}
*/
    ul.calendar-tabmenu li a:hover {
        position: relative;
        bottom: 3px;
    }
</style>
sample表示

<dl>
  <dt>説明</dt>
  <dd>${description}</dd>
</dl>

% if form:
  <div id="select_form">
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
% endif

${renderable.render()|n}
<script type="text/javascript">
  $(".calendar-tab").click(function(){
    var selected = $(".calendar-tab.selected");
    $("#calendar_"+selected.attr("month")).addClass("hidden");
    selected.removeClass("selected");

    var new_selected = $(this);
    new_selected.addClass("selected");
    $("#calendar_"+new_selected.attr("month")).removeClass("hidden");
  });
</script>
