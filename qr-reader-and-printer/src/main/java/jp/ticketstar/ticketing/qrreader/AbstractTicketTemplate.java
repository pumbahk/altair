package jp.ticketstar.ticketing.qrreader;

public abstract class AbstractTicketTemplate implements TicketTemplate {
	protected final int id;
	protected final String name;
	protected final TicketFormat ticketFormat;

	public int getId() {
		return id;
	}

	public String getName() {
		return name;
	}
	
	public TicketFormat getTicketFormat() {
		return ticketFormat;
	}

	public AbstractTicketTemplate(int id, String name, TicketFormat ticketFormat) {
		this.id = id;
		this.name = name;
		this.ticketFormat = ticketFormat;
	}
}
