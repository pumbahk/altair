package jp.ticketstar.ticketing.qrreader;

import java.util.Collections;
import java.util.Map;
import java.util.HashMap;

public class TicketImpl implements Ticket {
	final String seatId;
	final String orderedProductItemId;
	final String orderId;
	final Map<String, String> data;

	public String getSeatId() {
		return seatId;
	}

	public String getOrderedProductItemId() {
		return orderedProductItemId;
	}

	public String getOrderId() {
		return orderId;
	}

	public Map<String, String> getData() {
		return Collections.unmodifiableMap(data);
	}

	public TicketImpl(String seatId, String orderedProductItemId, String orderId, Map<String, String> data) {
		this.seatId = seatId;
		this.orderedProductItemId = orderedProductItemId;
		this.orderId = orderId;
		this.data = new HashMap<String, String>(data);
	}
}