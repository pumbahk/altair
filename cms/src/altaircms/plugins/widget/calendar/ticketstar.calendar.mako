<div class="calendar">
  <div id="detailSchedule">
	<h2><img src="/static/ticketstar/img/detail/title_schedule.gif" alt="公演日程" width="77" height="30" /></h2>
	<table>
	 <thead>
	   <tr>
		 <td class="month-col empty"/>
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
		%if week.month_changed:
		  <th class="month-col">
			<span class="month-main">${week.month}月</span>
		  </th>
		%else:
		  <td class="month-col empty"/>
		%endif
		%for de in week:
		  <td class="${de["day_class"]}">
            <span class="day">${de["day"]}&nbsp;</span>
			%for p in de["day_performances"]:
                  <% status= h.event.detect_performance_status(p)%>
	              <p class="${status}">
					<strong>${h.event.content_string_from_performance_status(status)}</strong>
					<a target="_blank" href="${h.link.get_purchase_page_from_performance(request,p)}">${p.start_on.strftime("%H:%M")}</a>
				  </p>
			%endfor
		  </td>   
		 %endfor
		 </tr>
	  %endfor
	 </tbody>
	</table>
  </div>
</div>
