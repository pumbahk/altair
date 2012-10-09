package jp.ticketstar.ticketing.qrreader;

import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.geom.AffineTransform;
import java.awt.print.PrinterJob;
import java.awt.print.PageFormat;
import java.awt.print.Printable;
import java.util.List;

import org.apache.batik.gvt.GraphicsNode;

import jp.ticketstar.ticketing.PrintableEventListener;
import jp.ticketstar.ticketing.PrintableEventSupport;

public class TicketPrintable implements Printable {
	protected final List<GraphicsNode> gvts;
	protected final AffineTransform transform;
	protected final PrintableEventSupport support;

	public TicketPrintable(List<GraphicsNode> gvts, PrinterJob job) {
		this(gvts, job, new AffineTransform());
	}
	
	public TicketPrintable(List<GraphicsNode> gvts, PrinterJob job, AffineTransform trans) {
		this.gvts = gvts;
		this.transform = trans;
		support = new PrintableEventSupport(this, job);
	}
	
	public int print(Graphics _g, PageFormat format, int pageIndex) {
		if (pageIndex >= gvts.size())
			return NO_SUCH_PAGE;
		Graphics2D g = (Graphics2D)_g;
		g.transform(transform);
		gvts.get(pageIndex).paint(g);
		support.firePagePrintedEvent(pageIndex);
		return PAGE_EXISTS;
	}

	public void addPrintableEventListener(PrintableEventListener lsnr) {
		support.addPrintableEventListener(lsnr);
	}

	public void removePrintableEventListener(PrintableEventListener lsnr) {
		support.removePrintableEventListener(lsnr);
	}

	public List<GraphicsNode> getGraphicsNodes() {
		return gvts;
	}

	public AffineTransform getTransform() {
		return transform;
	}
}