<% from altair.app.ticketing.orderreview.api import safe_get_contact_url %>
<div class="footer">
  <div class="footer-inner">
    <div class="footernav">
      <ul>
        <li><a class="first" href="http://www.ticketstar.jp/corporate" target="_blank">運営会社</a></li>
          <li><a href="${safe_get_contact_url(request, default='')}" target="_blank">お問い合わせ</a></li>
          <li><a href="http://www.ticketstar.jp/privacy" target="_blank">個人情報保護方針</a></li>
        <li><a class="last" href="http://www.ticketstar.jp/legal" target="_blank">特定商取引法に基づく表示</a></li>
      </ul>
    </div>
    <br class="clear">
    <div class="copyright">
      Copyright © 2010-2013 TicketStar Inc. All Rights Reserved. 
    </div>
  </div>
</div>

