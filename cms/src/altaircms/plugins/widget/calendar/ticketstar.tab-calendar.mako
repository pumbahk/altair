## todo: performanceのステータス表示

<%def name="calendar_table(cal, id, hidden)">
      <table id="${id}"${'style="display:none"'if not hidden else ""|n}>
       <thead>
         <tr>
           <th scope="col"  class="first">月</th>
           <th scope="col" >火</th>
           <th scope="col" >水</th>
           <th scope="col" >木</th>
           <th scope="col" >金</th>
           <th scope="col" >土</th>
           <th scope="col"  class="last">日</th>
         </tr>
       </thead>
       <tbody>
        %for week in cal:
          <tr>
          %for de in week:
            <td class="${de["day_class"]}">
              <span class="day">${de["day"]}&nbsp;</span>
              %for p in de["day_performances"]:
                  <% status= h.event.detect_performance_status(p)%>
	              <p class="${status}">
					<strong>${h.event.content_string_from_performance_status(status)}</strong>
					<a target="_blank" href="#">${p.start_on.strftime("%H:%M")}</a>
				  </p>
              %endfor
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

<div class="calendar">
<div id="detailSchedule">
  <h2><img src="/static/ticketstar/img/detail/title_schedule.gif" alt="公演日程" width="77" height="30" /></h2>

  <ul>
    %for visibility, m in zip(visbs0, months):
	  <li month="${gen_id(m)}" class="calendar-tab ${"active" if visibility else ""}"><a>${m[0]}年${m[1]}月</a></li> 
    %endfor
  </ul>

  %for visibility, m, cal in zip(visbs1, months, cals):
    ${calendar_table(cal, gen_id(m), visibility)}
  %endfor

	<script type="text/javascript" src="/static/ticketstar/js/jquery.flatheights.js"></script>
	<script type="text/javascript">
	$(function() {
	     // highlight selected month element
		$(".calendar-tab").click(function(){
		  var active = $(".calendar-tab.active");
		  $("#"+active.attr("month")).hide();
		  active.removeClass("active");

		  var new_active = $(this);
		  new_active.addClass("active");
		  $("#"+new_active.attr("month")).show();
		});

		$('#detailSchedule td').flatHeights();
	});
	</script>
</div>
</div>
