package jp.ticketstar.ticketing.qrreader;

import java.util.Map;

public interface Ticket {
	public String getSeatId();
	
	public String getOrderedProductItemId();

	public String getOrderId();

	public Map<String, String> getData();

}