package jp.ticketstar.ticketing.printing;

import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.geom.AffineTransform;
import java.awt.print.PageFormat;
import java.awt.print.Printable;

public class TicketPrintable implements Printable {
	final Pages tickets;
	final AffineTransform trans;

	public TicketPrintable(Pages tickets) {
		this(tickets, new AffineTransform());
	}
	
	public TicketPrintable(Pages tickets, AffineTransform trans) {
		this.tickets = tickets;
		this.trans = trans;
	}
	
	public int print(Graphics _g, PageFormat format, int pageIndex) {
		if (pageIndex >= tickets.size())
			return NO_SUCH_PAGE;
		Graphics2D g = (Graphics2D)_g;
		g.transform(trans);
		tickets.get(pageIndex).getGraphics().paint(g);
		return PAGE_EXISTS;
	}
}
