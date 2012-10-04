package jp.ticketstar.ticketing.qrreader;

import java.awt.geom.AffineTransform;
import java.awt.geom.Dimension2D;
import java.awt.print.PageFormat;
import java.awt.print.Paper;
import java.awt.print.PrinterJob;
import java.io.IOException;
import java.security.AccessController;
import java.security.PrivilegedAction;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import javax.print.PrintService;

import jp.ticketstar.ticketing.ApplicationException;
import jp.ticketstar.ticketing.qrreader.gui.IAppWindow;

import org.apache.batik.bridge.BridgeContext;
import org.apache.batik.bridge.GVTBuilder;
import org.apache.batik.bridge.UserAgent;
import org.apache.batik.bridge.UserAgentAdapter;
import org.apache.batik.dom.svg.SVGOMDocument;
import org.apache.batik.gvt.GraphicsNode;
import org.w3c.dom.svg.SVGDocument;

public class AppService {
	protected AppModel model;
	protected final UserAgent userAgent = new UserAgentAdapter();
	protected final BridgeContextFactory bridgeContextFactory = new DefaultBridgeContextFactory(userAgent);
	
	public AppService(AppModel model) {
		this.model = model;
	}

	public void setAppWindow(IAppWindow appWindow) {
		appWindow.bind(model);
	}

	protected TicketPrintable createTicketPrintable(PrinterJob job) {
		final List<GraphicsNode> svgs = new ArrayList<GraphicsNode>();
		final TicketTemplate template = model.getTicketTemplate();
		final GVTBuilder builder = new GVTBuilder();
		try {
			for (Ticket ticket: model.getTickets()) {
				final SVGDocument doc = template.buildSVGDocument(ticket);
				final BridgeContext ctx = bridgeContextFactory.createBridgeContext((SVGOMDocument)doc);
				svgs.add(builder.build(ctx, doc));
			}
		} catch (IOException e) {
			throw new ApplicationException(e);
		}
		return new TicketPrintable(
			svgs, job,
			new AffineTransform(72. / 90, 0, 0, 72. / 90, 0, 0)
		);
	}

	public void printAll() {
		AccessController.doPrivileged(new PrivilegedAction<Object>() {
			public Object run() {
				try {
					final PrinterJob job = PrinterJob.getPrinterJob();
					job.setPrintService(model.getPrintService());
					job.setPrintable(
						createTicketPrintable(job),
						createPageFormatFromTicketFormat(
							model.getTicketTemplate().getTicketFormat()));
					job.print();
				} catch (Exception e) {
					e.printStackTrace();
					throw new ApplicationException(e);
				}
				return null;
			}
		});
	}

	protected PageFormat createPageFormatFromTicketFormat(TicketFormat ticketFormat) {
		final PageFormat retval = new PageFormat(); 
		{
			final Paper paper = new Paper();
			final Dimension2D size = ticketFormat.getSize();
			final double width = size.getWidth(), height = size.getHeight();
			paper.setImageableArea(0, 0, width, height);
			paper.setSize(width, height);
			retval.setPaper(paper);
		}
		return retval;
	}
	
	public void addTicket(Ticket ticket) {
		model.getTickets().add(ticket);
	}

	public void removeTicket(Ticket ticket) {
		model.getTickets().remove(ticket);
	}

	public List<TicketTemplate> getTicketTemplates() {
		return Collections.unmodifiableList(model.getTicketTemplates());
	}

	public TicketTemplate getTicketTemplate() {
		return model.getTicketTemplate();
	}

	public void setTicketTemplate(TicketTemplate template) {
		model.setTicketTemplate(template);
	}
	
	public List<PrintService> getPrintServices() {
		return Collections.unmodifiableList(model.getPrintServices());
	}

	public PrintService getPrintService() {
		return model.getPrintService();
	}
	
	public void setPrintService(PrintService service) {
		model.setPrintService(service);
	}
}
