package jp.ticketstar.ticketing.printing;

import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.geom.AffineTransform;
import java.awt.print.PageFormat;
import java.awt.print.Printable;

public class TicketPrintable implements Printable {
	final Tickets tickets;
	final AffineTransform trans;

	public TicketPrintable(Tickets tickets) {
		this(tickets, new AffineTransform());
	}
	
	public TicketPrintable(Tickets tickets, AffineTransform trans) {
		this.tickets = tickets;
		this.trans = trans;
	}
	
	public int print(Graphics _g, PageFormat format, int pageIndex) {
		if (pageIndex >= tickets.size())
			return NO_SUCH_PAGE;
		Graphics2D g = (Graphics2D)_g;
		AffineTransform prevTrans = g.getTransform();
		g.setTransform(trans);
		tickets.get(pageIndex).getGraphics().paint(g);
		g.setTransform(prevTrans);
		return PAGE_EXISTS;
	}
}
