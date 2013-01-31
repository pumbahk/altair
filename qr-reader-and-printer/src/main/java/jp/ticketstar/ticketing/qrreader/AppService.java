package jp.ticketstar.ticketing.qrreader;

import java.awt.geom.AffineTransform;
import java.awt.print.PrinterJob;
import java.io.IOException;
import java.security.AccessController;
import java.security.PrivilegedAction;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import javax.print.PrintService;

import jp.ticketstar.ticketing.ApplicationException;
import jp.ticketstar.ticketing.PrintableEvent;
import jp.ticketstar.ticketing.PrintableEventListener;
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

	protected TicketPrintable createTicketPrintable(PrinterJob job, final List<Ticket> tickets) {
		final List<GraphicsNode> svgs = new ArrayList<GraphicsNode>();
		final TicketTemplate template = model.getTicketTemplate();
		final GVTBuilder builder = new GVTBuilder();
		try {
			for (Ticket ticket: tickets) {
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
					final List<Ticket> tickets = new ArrayList<Ticket>(model.getTickets());
					final TicketPrintable printable = createTicketPrintable(job, tickets);
					printable.addPrintableEventListener(new PrintableEventListener() {
						@Override
						public void pagePrinted(PrintableEvent evt) {
							model.getTickets().remove(tickets.get(evt.getPageIndex()));
						}
					});
					job.setPrintable(printable, model.getPageFormat());
					job.print();
				} catch (Exception e) {
					e.printStackTrace();
					throw new ApplicationException(e);
				}
				return null;
			}
		});
	}

	public void addTicket(Ticket ticket) {
		model.getTickets().add(ticket);
	}

	public void removeTicket(Ticket ticket) {
		model.getTickets().remove(ticket);
	}

	public void removeTicketAll(){
		model.getTickets().removeAll();
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

	public List<OurPageFormat> getPageFormats() {
		return Collections.unmodifiableList(model.getPageFormats());
	}

	public OurPageFormat getPageFormat() {
		return model.getPageFormat();
	}
	
	public void setPageFormat(OurPageFormat pageFormat) {
		model.setPageFormat(pageFormat);
	}
}
