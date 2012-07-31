<%def name="calendar_table(cal, id, hidden)">
<table height="390px" id="${id}"${'style="display:none"'if not hidden else ""|n}>
 <thead>
   <tr>
     <th class="first">月</th>
     <th>火</th>
     <th>水</th>
     <th>木</th>
     <th>金</th>
     <th>土</th>
     <th class="last">日</th>
   </tr>
 </thead>
 <tbody>
  %for week in cal:
    <tr>
    %for de in week:
      <td class="${de["day_class"]}">
        <span class="day">${de["day"]}</span>
        <ul>
        %for p in de["day_performances"]:
          <% status= calendar_status.get_status(p)%>
          <li class="${status["class"]}">
			<!-- <strong>${status["string"]}</strong> -->
            <a href="${h.link.get_purchase_page_from_performance(request,p)}}">${p.start_on.strftime("%H:%M")}</a>
            <p>${p.calendar_content or u""}</p></li>
        %endfor
        </ul>
      </td>   
     %endfor
     </tr>
  %endfor
 </tbody>
</table>
</%def>

<%
import itertools
visbs0, visbs1 = itertools.tee(visibilities)

def gen_id(y_and_m):
   return "calendar_%d%d" % (y_and_m[0], y_and_m[1])
%>

<div class="calendar2"  id="performance-calendar">
  <div class="month-tab">
	  %for visibility, m in zip(visbs0, months):
		<span month="${gen_id(m)}" class="calendar-tab ${"current" if visibility else ""}"><a>${m[0]}年${m[1]}月</a></span>
	  %endfor
  </div>
  <div class="calendarInner">
	%for visibility, m, cal in zip(visbs1, months, cals):
	  ${calendar_table(cal, gen_id(m), visibility)}
	%endfor
  </div>
	  <script type="text/javascript">
	  $(function() {
		   // highlight selected month element
		  $(".calendar-tab").click(function(){
			var current = $(".calendar-tab.current");
			$("#"+current.attr("month")).hide();
			current.removeClass("current");

			var new_current = $(this);
			new_current.addClass("current");
			$("#"+new_current.attr("month")).show();
		  });
	  });
	  </script>
</div>
