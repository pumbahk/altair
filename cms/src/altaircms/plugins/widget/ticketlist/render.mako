## ticketlist widget output template
## 
## todo: link

<div class="detailBox">
  <div class="detailBoxInner">
	<h2><img src="/static/ticketstar/img/detail/title_price.gif" alt="チケット価格" width="107" height="30" /></h2>
	<table id="ticketPrice1" summary="チケット価格表">
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

<%doc>
<div class="ticketlist-widget">
  <table class="ticketlist">
	<colgroup>
	  <col/>
	  <col/>
	</colgroup>
	<tbody>
	    <tr>
		  <td class="head">席種</td><td class="head">料金</td>
		</tr>
	  % for ticket in tickets:
	    <tr>
		  <td>${ ticket.seattype }</td>
          <td>￥${ h.event.price_format(ticket.price) }</td>
		</tr>
	  % endfor
	</tbody>
  </table>
</div>
</%doc>
