<div class="box">
<table class="table">
  <thead>
	<tr>
	  <th></th>
	  <th>名前</th>
	  <th>販売条件</th>
	  <th>適用期間</th>
	  <th>券種</th>
	  <th>席種</th>
	  <th>価格</th>
	</tr>
  </thead>
  <tbody>
     %for sale in sales:
<%
tickets = sale.tickets
tickets_size = len(tickets)
 %>
       <tr>
         <td rowspan="${ tickets_size }">
           <input type="radio" name="object_id" value="${sale.id}">
         </td>
         <td rowspan="${ tickets_size }">${ sale.name }</td>
         <td rowspan="${ tickets_size }">${sale.jkind}</td>
         <td rowspan="${ tickets_size }">${ h.base.jterm(sale.start_on,sale.end_on) if sale.start_on and sale.end_on else u"~"}</td>
%if len(tickets) <= 0:
       </tr>
%else:
         <td><a href="${request.route_path("ticket_update",action="input",id=tickets[0].id)}">${tickets[0].name}</a></td>
         <td>${tickets[0].seattype}</td>
         <td>${tickets[0].price}</td>
       </tr>
       %for t in tickets[1:]:
         <tr>
         <td><a href="${request.route_path("ticket_update",action="input",id=t.id)}">${t.name}</a></td>
         <td>${t.seattype}</td>
         <td>${t.price}</td>
         </tr>
       %endfor
%endif
     %endfor
  </tbody>
</table>
  <div class="btn-group">
	<a href="${request.route_path("sale_update",action="input",id="__id__")}" class="btn action">
	  <i class="icon-pencil"></i> 編集
	</a>
	<button class="btn dropdown-toggle" data-toggle="dropdown">
		<span class="caret"></span>
	</button>
	<ul class="dropdown-menu">
	  <li>
		<a href="${request.route_path("sale_update",action="input",id="__id__")}"  class="action">
		  <i class="icon-minus"></i> 編集
		</a>
	  </li>
	  <li>
		<a href="${request.route_path("sale_create",action="input",_query=dict(event=event.id))}">
		  <i class="icon-minus"></i> 新規作成
		</a>
	  </li>
	  <li>
		<a href="${request.route_path("sale_delete",action="confirm",id="__id__")}"  class="action">
		  <i class="icon-minus"></i> 削除
		</a>
	  </li>
	</ul>
  </div>
</div>
