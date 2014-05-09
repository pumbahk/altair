package jp.ticketstar.ticketing.qrreader;

import java.util.Collections;
import java.util.Map;
import java.util.HashMap;

public class TicketImpl implements Ticket {
    final String ticketTemplateId;
	final String seatId;
	final String orderedProductItemTokenId;
	final String orderedProductItemId;
	final String orderId;
	final Map<String, Object> data;

    public String getTicketTemplateId() {
        return ticketTemplateId;
    }

	public String getSeatId() {
		return seatId;
	}

	public String getOrderedProductItemTokenId() {
		return orderedProductItemTokenId;
	}
	
	public String getOrderedProductItemId() {
		return orderedProductItemId;
	}

	public String getOrderId() {
		return orderId;
	}

	public Map<String, Object> getData() {
		return Collections.unmodifiableMap(data);
	}

	public TicketImpl(String ticketTemplateId, String seatId, String orderedProductItemTokenId, String orderedProductItemId, String orderId, Map<String, Object> data) {
        this.ticketTemplateId = ticketTemplateId;
		this.seatId = seatId;
		this.orderedProductItemTokenId = orderedProductItemTokenId;
		this.orderedProductItemId = orderedProductItemId;
		this.orderId = orderId;
		this.data = new HashMap<String, Object>(data);
	}
}
