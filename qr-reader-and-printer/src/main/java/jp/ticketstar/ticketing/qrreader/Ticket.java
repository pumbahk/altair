package jp.ticketstar.ticketing.qrreader;

import java.util.Map;

public interface Ticket {
    public String getTicketTemplateId();

	public String getSeatId();

	public String getOrderedProductItemTokenId();
	
	public String getOrderedProductItemId();

	public String getOrderId();

	public Map<String, Object> getData();

}
