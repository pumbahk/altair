package jp.ticketstar.ticketing.qrreader;

public abstract class AbstractTicketTemplate implements TicketTemplate {
	protected final String id;
	protected final String name;
	protected final TicketFormat ticketFormat;

	public String getId() {
		return id;
	}

	public String getName() {
		return name;
	}
	
	public TicketFormat getTicketFormat() {
		return ticketFormat;
	}

	public AbstractTicketTemplate(String id, String name, TicketFormat ticketFormat) {
		this.id = id;
		this.name = name;
		this.ticketFormat = ticketFormat;
	}
}
