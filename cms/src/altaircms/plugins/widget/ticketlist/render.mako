## ticketlist widget output template
## 

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

<%doc>
<div class="ticketlist-widget">
  <table width="190" cellspacing="0" cellpadding="0" border="0" style="width: 143pt; border-collapse: collapse;">
	<colgroup>
	  <col width="96" style="width: 72pt;"/>
	  <col width="94" style="width: 71pt;"/>
	</colgroup><tbody>
	  <tr height="18" style="height: 13.5pt;">
		<td width="96" height="18" class="xl65" style="border-width: 0.5pt; border-style: solid; border-color: windowtext; background-color: rgb(191, 191, 191); width: 72pt; height: 13.5pt;"><font size="3" face="ＭＳ Ｐゴシック">席種</font></td>
		<td width="94" class="xl65" style="border-width: 0.5pt 0.5pt 0.5pt medium; border-style: solid solid solid none; border-color: windowtext; background-color: rgb(191, 191, 191); width: 71pt;"><font size="3" face="ＭＳ Ｐゴシック">料金</font></td></tr>
	  <tr height="18" style="height: 13.5pt;">
		<td height="18" class="xl63" style="border-width: medium 0.5pt 0.5pt; border-style: none solid solid; border-color: windowtext; background-color: transparent; height: 13.5pt;"><font size="3" face="ＭＳ Ｐゴシック">S席</font></td>
		<td align="right" class="xl64" style="border-width: medium 0.5pt 0.5pt medium; border-style: none solid solid none; border-color: windowtext; background-color: transparent;"><font size="3" face="ＭＳ Ｐゴシック">¥10,000</font></td></tr>
	  <tr height="18" style="height: 13.5pt;">

		<td height="18" class="xl63" style="border-width: medium 0.5pt 0.5pt; border-style: none solid solid; border-color: windowtext; background-color: transparent; height: 13.5pt;"><font size="3" face="ＭＳ Ｐゴシック">A席</font></td>
		<td align="right" class="xl64" style="border-width: medium 0.5pt 0.5pt medium; border-style: none solid solid none; border-color: windowtext; background-color: transparent;"><font size="3" face="ＭＳ Ｐゴシック">¥8,000</font></td></tr>
	  <tr height="18" style="height: 13.5pt;">
		<td height="18" class="xl63" style="border-width: medium 0.5pt 0.5pt; border-style: none solid solid; border-color: windowtext; background-color: transparent; height: 13.5pt;"><font size="3" face="ＭＳ Ｐゴシック">B席</font></td>
		<td align="right" class="xl64" style="border-width: medium 0.5pt 0.5pt medium; border-style: none solid solid none; border-color: windowtext; background-color: transparent;"><font size="3" face="ＭＳ Ｐゴシック">¥6,000</font></td></tr>
  </tbody></table>
</div>
</%doc>
