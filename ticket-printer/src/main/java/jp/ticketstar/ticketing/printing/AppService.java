package jp.ticketstar.ticketing.printing;

import java.awt.Cursor;
import java.awt.Point;
import java.awt.geom.AffineTransform;
import java.awt.geom.Dimension2D;
import java.net.URI;

import javax.swing.JFileChooser;

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
}
