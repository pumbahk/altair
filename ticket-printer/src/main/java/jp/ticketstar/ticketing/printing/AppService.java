package jp.ticketstar.ticketing.printing;

import java.awt.Cursor;
import java.awt.Point;
import java.awt.geom.AffineTransform;
import java.awt.geom.Dimension2D;
import java.awt.print.Printable;
import java.awt.print.PrinterJob;
import java.io.File;
import java.net.URI;

import javax.swing.JFileChooser;

import jp.ticketstar.ticketing.printing.svg.ExtendedSVG12BridgeContext;
import jp.ticketstar.ticketing.printing.svg.ExtendedSVG12OMDocument;
import jp.ticketstar.ticketing.printing.svg.OurDocumentLoader;

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

public class AppService extends SVGUserAgentGUIAdapter implements UserAgent {
	AppWindowModel appWindowModel;
	SVGDocumentLoader documentLoader;
	
	public AppService(AppWindowModel appWindowModel) {
		super(null);
		this.appWindowModel = appWindowModel;
	}

	public void setAppWindow(AppWindow appWindow) {
		parentComponent = appWindow.getFrame();
		appWindow.bind(appWindowModel);
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

	public void loadDocument(URI uri) {
		if (documentLoader != null)
			return;
		final OurDocumentLoader loader = new OurDocumentLoader(this);
		documentLoader = new SVGDocumentLoader(uri.toString(), loader);
		final ExtendedSVG12BridgeContext bridgeContext = new ExtendedSVG12BridgeContext(this, loader);
		documentLoader.addSVGDocumentLoaderListener(new SVGDocumentLoaderListener() {
			public void documentLoadingCancelled(SVGDocumentLoaderEvent arg0) {
				documentLoader = null;
				displayError("Load cancelled");
			}

			public void documentLoadingCompleted(SVGDocumentLoaderEvent arg0) {
				documentLoader = null;
				// TODO: do it async!
				try {
					bridgeContext.setInteractive(false);
					bridgeContext.setDynamic(false);
					appWindowModel.setTicketSetModel(new TicketSetModel(bridgeContext, (ExtendedSVG12OMDocument)arg0.getSVGDocument()));
				} catch (Exception e) {
					e.printStackTrace(System.err);
					displayError("Failed to load document\nReason: " + e);
				}
			}

			public void documentLoadingFailed(SVGDocumentLoaderEvent arg0) {
				documentLoader = null;
				((SVGDocumentLoader)arg0.getSource()).getException().printStackTrace(System.err);
				displayError("Failed to load document\nReason: " + ((SVGDocumentLoader)arg0.getSource()).getException());
			}

			public void documentLoadingStarted(SVGDocumentLoaderEvent arg0) {
			}
		});
		documentLoader.start();
	}

	public void printAll() {
		try {
			final PrinterJob job = PrinterJob.getPrinterJob();
			job.setPrintService(appWindowModel.getPrintService());
			final Printable printable = new TicketPrintable(
				appWindowModel.getTicketSetModel().getTickets(),
				new AffineTransform(1, 0, 0, 1, 0, 0)
			);
			job.setPrintable(printable);
			if (job.printDialog())
				job.print();
		} catch (Exception e) {
			displayError("Failed to print tickets\nReason: " + e);
		}
	}
}
