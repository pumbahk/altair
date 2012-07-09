<%def name="calendar_table(cal)">
      <table>
       <thead>
         <tr>
           <td class="empty"/>
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
          %if week.month_changed:
            <th class="month">
              <span class="month-header"><span class="month-header-content"/></span></span>
              <span class="month-main">${week.month}月</span>
              <span class="month-footer"><span class="month-footer-content"/></span>
            </th>
          %else:
            <td class="empty"/>
          %endif
          %for de in week:
            <td class="${de["day_class"]}">
              <span class="day">${de["day"]}</span>
              <ul>
              %for p in de["day_performances"]:
                <li><span class="serial"><a href="#performance-${p.id}">00</a></span>
                  <a href="#">${p.start_on.strftime("%H:%M")}</a>
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
%>

<div class="calendar" id="performance-calendar">
  <ul class="calendar-tabmenu">
    %for visibility, m in zip(visbs0, months):
	  <li><a month="${m}" class="calendar-tab ${"selected" if visibility else ""}">${m}月</a></li> 
    %endfor
  </ul>
  <div class="clear"/>
  %for visibility, m, cal in zip(visbs1, months, cals):
    <div id="calendar_${m}" class="calendar-element ${"" if visibility else "hidden"}">
	  ${calendar_table(cal)}
    </div>
  %endfor
</div>

