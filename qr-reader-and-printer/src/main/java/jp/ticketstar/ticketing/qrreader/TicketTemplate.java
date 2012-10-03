package jp.ticketstar.ticketing.qrreader;

import java.io.IOException;

import org.w3c.dom.svg.SVGDocument;

public interface TicketTemplate {
	public int getId();
	
	public String getName();
	
	public TicketFormat getTicketFormat();

	public SVGDocument buildSVGDocument(Ticket ticket) throws IOException;
}