## ticketlist widget output template
## 
## todo: link

<h2><img src="/static/ticketstar/img/detail/title_price.gif" alt="チケット価格" width="107" height="30"/>(${sale.jkind if sale else u""})</h2>
<div class="detailBox">
  <div class="detailBoxInner">
	<table id="ticketPrice1" summary="チケット価格表(${sale.jkind if sale else u""})">
	  % for ticket in tickets:
	    <tr>
		  <th scope="row"><a href="#">${ ticket.seattype }</a></th>
		  <td></td>
          <td>${ h.event.price_format(ticket.price) }円</td>
		</tr>
	  % endfor
	</table>
  </div>
</div>
