package jp.ticketstar.ticketing.printing;

import java.awt.Cursor;
import java.awt.Point;
import java.awt.geom.AffineTransform;
import java.awt.geom.Dimension2D;
import java.awt.print.PrinterJob;
import java.beans.PropertyChangeListener;
import java.net.URI;
import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;
import java.util.logging.Logger;

import javax.print.PrintService;

import jp.ticketstar.ticketing.LoggingUtils;
import jp.ticketstar.ticketing.printing.gui.IAppWindow;
import jp.ticketstar.ticketing.svg.ExtendedSVG12BridgeContext;
import jp.ticketstar.ticketing.svg.ExtendedSVG12OMDocument;
import jp.ticketstar.ticketing.svg.OurDocumentLoader;

import org.apache.batik.bridge.BridgeExtension;
import org.apache.batik.bridge.UserAgent;
import org.apache.batik.gvt.event.EventDispatcher;
import org.apache.batik.gvt.text.Mark;
import org.apache.batik.swing.svg.SVGDocumentLoader;
import org.apache.batik.swing.svg.SVGDocumentLoaderEvent;
import org.apache.batik.swing.svg.SVGDocumentLoaderListener;
import org.apache.batik.swing.svg.SVGUserAgentGUIAdapter;
import org.w3c.dom.Element;
import org.w3c.dom.svg.SVGAElement;
import org.w3c.dom.svg.SVGDocument;

public abstract class BasicAppService extends SVGUserAgentGUIAdapter implements MinimumAppService, UserAgent {
	private static final Logger logger = Logger.getLogger(BasicAppService.class.getName());
	protected AppModel model;
	protected volatile SVGDocumentLoader documentLoader;
	protected IAppWindow appWindow;
	protected LinkedList<Runnable> pendingTasks = new LinkedList<Runnable>();

	public class LoaderListener implements SVGDocumentLoaderListener {
		ExtendedSVG12BridgeContext bridgeContext;
		
		private void next() {
			appWindow.setInteractionEnabled(true);
			BasicAppService.this.documentLoader = null;
			BasicAppService.this.doPendingTasks();
		}
	
		public void documentLoadingCancelled(SVGDocumentLoaderEvent arg0) {
			logger.info("load canceled");
			next();
			displayError("Load canceled");
		}

		public void documentLoadingCompleted(SVGDocumentLoaderEvent arg0) {
			// TODO: do it async!
			try {
				bridgeContext.setInteractive(false);
				bridgeContext.setDynamic(false);
				BasicAppService.this.model.setPageSetModel(new PageSetModel(bridgeContext, (ExtendedSVG12OMDocument)arg0.getSVGDocument()));
			} catch (Exception e) {
				e.printStackTrace();
				displayError("Failed to load document\nReason: " + e);
			} finally {
				logger.info("Load completed");
				next();
			}
		}

		public void documentLoadingFailed(SVGDocumentLoaderEvent arg0) {
			logger.severe(LoggingUtils.formatException(((SVGDocumentLoader)arg0.getSource()).getException()));
			next();
			displayError("Failed to load document\nReason: " + ((SVGDocumentLoader)arg0.getSource()).getException());
		}

		public void documentLoadingStarted(SVGDocumentLoaderEvent arg0) {
			logger.info("load started");
			appWindow.setInteractionEnabled(false);
		}

		public LoaderListener(ExtendedSVG12BridgeContext bridgeContext) {
			this.bridgeContext = bridgeContext;
		}
	}

	public void setAppWindow(IAppWindow appWindow) {
		parentComponent = appWindow.getFrame();
		appWindow.bind(model);
		this.appWindow = appWindow;
	}

	public void deselectAll() {
		// TODO Auto-generated method stub
		
	}

	public SVGDocument getBrokenLinkDocument(Element arg0, String arg1,
			String arg2) {
		// TODO Auto-generated method stub
		return null;
	}

	public Point getClientAreaLocationOnScreen() {
		// TODO Auto-generated method stub
		return null;
	}

	public EventDispatcher getEventDispatcher() {
		// TODO Auto-generated method stub
		return null;
	}

	public AffineTransform getTransform() {
		// TODO Auto-generated method stub
		return null;
	}

	public Dimension2D getViewportSize() {
		// TODO Auto-generated method stub
		return null;
	}

	public boolean hasFeature(String arg0) {
		// TODO Auto-generated method stub
		return false;
	}

	public void openLink(SVGAElement arg0) {
		// TODO Auto-generated method stub
		
	}

	public void registerExtension(BridgeExtension arg0) {
		// TODO Auto-generated method stub
		
	}

	public void setSVGCursor(Cursor arg0) {
		// TODO Auto-generated method stub
		
	}

	public void setTextSelection(Mark arg0, Mark arg1) {
		// TODO Auto-generated method stub
		
	}

	public void setTransform(AffineTransform arg0) {
		// TODO Auto-generated method stub
		
	}

	public synchronized void loadDocument(URI uri) {
		if (this.documentLoader != null)
			throw new IllegalStateException("Document is being loaded");
		final OurDocumentLoader loader = new OurDocumentLoader(this);
		final SVGDocumentLoader documentLoader = new SVGDocumentLoader(uri.toString(), loader);
		this.documentLoader = documentLoader;
		documentLoader.addSVGDocumentLoaderListener(new LoaderListener(new ExtendedSVG12BridgeContext(this, loader)));
		documentLoader.start();
	}
	
	protected TicketPrintable createTicketPrintable(PrinterJob job) {
		return new TicketPrintable(
			new ArrayList<Page>(model.getPageSetModel().getPages()), job,
			new AffineTransform(72. / 90, 0, 0, 72. / 90, 0, 0)
		);
	}

	public List<OurPageFormat> getPageFormats() {
		return model.getPageFormats() == null ?
			null: new ArrayList<OurPageFormat>(model.getPageFormats());
	}

	public OurPageFormat getPageFormat() {
		return model.getPageFormat();
	}
	
	public synchronized void setPageFormat(OurPageFormat pageFormat) {
		if (this.documentLoader != null)
			throw new IllegalStateException("Document is being loaded");
		model.setPageFormat(pageFormat);
	}

	public void addListenerForPageFormat(PropertyChangeListener listener) {
		model.addPropertyChangeListener("pageFormat", listener);
	}
	
	public List<PrintService> getPrintServices() {
		return model.getPrintServices() == null ?
			null: new ArrayList<PrintService>(model.getPrintServices());
	}

	public PrintService getPrintService() {
		return model.getPrintService();
	}
	
	public void setPrintService(PrintService printService) {
		model.setPrintService(printService);
	}

	public void addListenerForPrintService(PropertyChangeListener listener) {
		model.addPropertyChangeListener("printService", listener);
	}

	public List<Page> getPages() {
		final PageSetModel pageSetModel = model.getPageSetModel();
		return pageSetModel == null ? null: new ArrayList<Page>(pageSetModel.getPages());
	}

	public void addListenerForPages(PropertyChangeListener listener) {
		model.addPropertyChangeListener("pageSetModel", listener);
	}

	protected void doPendingTasks() {
		logger.entering(getClass().getName(), "doPendingTasks()");
		ArrayList<Runnable> tasksToBeDone = null;
		synchronized (pendingTasks) {
			tasksToBeDone = new ArrayList<Runnable>(pendingTasks);
			pendingTasks.clear();
		}	
		
		for (final Runnable task: tasksToBeDone) {
			try {
				task.run();
			} catch (Exception e) {
				logger.severe(LoggingUtils.formatException(e));
			}
		}
		logger.exiting(getClass().getName(), "doPendingTasks()");
	}
	
	public void invokeWhenDocumentReady(Runnable runnable) {
		logger.entering(getClass().getName(), "invokeWhenDocumentReady()");
		synchronized (pendingTasks) {
			pendingTasks.add(runnable);
		}
		if (documentLoader == null)
			doPendingTasks();
		logger.exiting(getClass().getName(), "invokeWhenDocumentReady()");
	}

	public BasicAppService(AppModel model) {
		super(null);
		this.model = model;
	}
}
