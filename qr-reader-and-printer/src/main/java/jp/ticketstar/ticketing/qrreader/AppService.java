package jp.ticketstar.ticketing.qrreader;

import java.awt.Cursor;
import java.awt.Point;
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
import org.apache.batik.bridge.BridgeExtension;
import org.apache.batik.bridge.ExternalResourceSecurity;
import org.apache.batik.bridge.GVTBuilder;
import org.apache.batik.bridge.ScriptSecurity;
import org.apache.batik.bridge.UserAgent;
import org.apache.batik.dom.svg.SVGOMDocument;
import org.apache.batik.gvt.event.EventDispatcher;
import org.apache.batik.gvt.text.Mark;
import org.apache.batik.util.ParsedURL;
import org.apache.batik.gvt.GraphicsNode;
import org.w3c.dom.Element;
import org.w3c.dom.svg.SVGAElement;
import org.w3c.dom.svg.SVGDocument;

public class AppService {
	protected AppModel model;
	protected final UserAgent userAgent = new UserAgent() {
		@Override
		public EventDispatcher getEventDispatcher() {
			// TODO Auto-generated method stub
			return null;
		}
	
		@Override
		public Dimension2D getViewportSize() {
			// TODO Auto-generated method stub
			return null;
		}
	
		@Override
		public void displayError(Exception ex) {
			// TODO Auto-generated method stub
			
		}
	
		@Override
		public void displayMessage(String message) {
			// TODO Auto-generated method stub
			
		}
	
		@Override
		public void showAlert(String message) {
			// TODO Auto-generated method stub
			
		}
	
		@Override
		public String showPrompt(String message) {
			// TODO Auto-generated method stub
			return null;
		}
	
		@Override
		public String showPrompt(String message, String defaultValue) {
			// TODO Auto-generated method stub
			return null;
		}
	
		@Override
		public boolean showConfirm(String message) {
			// TODO Auto-generated method stub
			return false;
		}
	
		@Override
		public float getPixelUnitToMillimeter() {
			// TODO Auto-generated method stub
			return 0;
		}
	
		@Override
		public float getPixelToMM() {
			// TODO Auto-generated method stub
			return 0;
		}
	
		@Override
		public float getMediumFontSize() {
			// TODO Auto-generated method stub
			return 0;
		}
	
		@Override
		public float getLighterFontWeight(float f) {
			// TODO Auto-generated method stub
			return 0;
		}
	
		@Override
		public float getBolderFontWeight(float f) {
			// TODO Auto-generated method stub
			return 0;
		}
	
		@Override
		public String getDefaultFontFamily() {
			// TODO Auto-generated method stub
			return null;
		}
	
		@Override
		public String getLanguages() {
			// TODO Auto-generated method stub
			return null;
		}
	
		@Override
		public String getUserStyleSheetURI() {
			// TODO Auto-generated method stub
			return null;
		}
	
		@Override
		public void openLink(SVGAElement elt) {
			// TODO Auto-generated method stub
			
		}
	
		@Override
		public void setSVGCursor(Cursor cursor) {
			// TODO Auto-generated method stub
			
		}
	
		@Override
		public void setTextSelection(Mark start, Mark end) {
			// TODO Auto-generated method stub
			
		}
	
		@Override
		public void deselectAll() {
			// TODO Auto-generated method stub
			
		}
	
		@Override
		public String getXMLParserClassName() {
			// TODO Auto-generated method stub
			return null;
		}
	
		@Override
		public boolean isXMLParserValidating() {
			// TODO Auto-generated method stub
			return false;
		}
	
		@Override
		public AffineTransform getTransform() {
			// TODO Auto-generated method stub
			return null;
		}
	
		@Override
		public void setTransform(AffineTransform at) {
			// TODO Auto-generated method stub
			
		}
	
		@Override
		public String getMedia() {
			// TODO Auto-generated method stub
			return null;
		}
	
		@Override
		public String getAlternateStyleSheet() {
			// TODO Auto-generated method stub
			return null;
		}
	
		@Override
		public Point getClientAreaLocationOnScreen() {
			// TODO Auto-generated method stub
			return null;
		}
	
		@Override
		public boolean hasFeature(String s) {
			// TODO Auto-generated method stub
			return false;
		}
	
		@Override
		public boolean supportExtension(String s) {
			// TODO Auto-generated method stub
			return false;
		}
	
		@Override
		public void registerExtension(BridgeExtension ext) {
			// TODO Auto-generated method stub
			
		}
	
		@Override
		public void handleElement(Element elt, Object data) {
			// TODO Auto-generated method stub
			
		}
	
		@Override
		public ScriptSecurity getScriptSecurity(String scriptType,
				ParsedURL scriptURL, ParsedURL docURL) {
			// TODO Auto-generated method stub
			return null;
		}
	
		@Override
		public void checkLoadScript(String scriptType, ParsedURL scriptURL,
				ParsedURL docURL) throws SecurityException {
			// TODO Auto-generated method stub
			
		}
	
		@Override
		public ExternalResourceSecurity getExternalResourceSecurity(
				ParsedURL resourceURL, ParsedURL docURL) {
			// TODO Auto-generated method stub
			return null;
		}
	
		@Override
		public void checkLoadExternalResource(ParsedURL resourceURL,
				ParsedURL docURL) throws SecurityException {
			// TODO Auto-generated method stub
			
		}
	
		@Override
		public SVGDocument getBrokenLinkDocument(Element e, String url,
				String message) {
			// TODO Auto-generated method stub
			return null;
		}
	};
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
