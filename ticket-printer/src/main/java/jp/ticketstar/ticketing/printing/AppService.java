package jp.ticketstar.ticketing.printing;

import java.awt.Cursor;
import java.awt.Point;
import java.awt.geom.AffineTransform;
import java.awt.geom.Dimension2D;
import java.awt.print.PrinterJob;
import java.io.File;
import java.net.URI;
import java.security.AccessController;
import java.security.PrivilegedAction;
import java.util.ArrayList;

import javax.swing.JFileChooser;

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
import org.apache.batik.util.HaltingThread;
import org.w3c.dom.Element;
import org.w3c.dom.svg.SVGAElement;
import org.w3c.dom.svg.SVGDocument;

public class AppService extends SVGUserAgentGUIAdapter implements UserAgent {
	protected AppModel model;
	protected HaltingThread documentLoader;

	protected class LoaderListener implements SVGDocumentLoaderListener {
		ExtendedSVG12BridgeContext bridgeContext;
		
		public void documentLoadingCancelled(SVGDocumentLoaderEvent arg0) {
			AppService.this.documentLoader = null;
			displayError("Load cancelled");
		}

		public void documentLoadingCompleted(SVGDocumentLoaderEvent arg0) {
			AppService.this.documentLoader = null;
			// TODO: do it async!
			try {
				bridgeContext.setInteractive(false);
				bridgeContext.setDynamic(false);
				model.setPageSetModel(new PageSetModel(bridgeContext, (ExtendedSVG12OMDocument)arg0.getSVGDocument()));
			} catch (Exception e) {
				e.printStackTrace();
				displayError("Failed to load document\nReason: " + e);
			}
		}

		public void documentLoadingFailed(SVGDocumentLoaderEvent arg0) {
			AppService.this.documentLoader = null;
			((SVGDocumentLoader)arg0.getSource()).getException().printStackTrace();
			displayError("Failed to load document\nReason: " + ((SVGDocumentLoader)arg0.getSource()).getException());
		}

		public void documentLoadingStarted(SVGDocumentLoaderEvent arg0) {
			System.out.println("load started!!");
		}

		public LoaderListener(ExtendedSVG12BridgeContext bridgeContext) {
			this.bridgeContext = bridgeContext;
		}
	}
	
	public AppService(AppModel model) {
		super(null);
		this.model = model;
	}

	public void setAppWindow(IAppWindow appWindow) {
		parentComponent = appWindow.getFrame();
		appWindow.bind(model);
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

	public void openFileDialog() {
		JFileChooser chooser = new JFileChooser();
		chooser.setCurrentDirectory(new File(System.getProperty("user.dir")));
		if (chooser.showOpenDialog(parentComponent) == JFileChooser.APPROVE_OPTION) {
			loadDocument(chooser.getSelectedFile().toURI());
		}
	}

	public synchronized void loadDocument(URI uri) {
		if (this.documentLoader != null)
			return;
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

	public void printAll() {
		AccessController.doPrivileged(new PrivilegedAction<Object>() {
			public Object run() {
				try {
					final PrinterJob job = PrinterJob.getPrinterJob();
					job.setPrintService(model.getPrintService());
					job.setPrintable(createTicketPrintable(job), model.getPageFormat());
					job.print();
				} catch (Exception e) {
					displayError("Failed to print tickets\nReason: " + e);
				}
				return null;
			}
		});
	}
}
