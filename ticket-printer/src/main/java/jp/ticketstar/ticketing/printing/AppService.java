package jp.ticketstar.ticketing.printing;

import java.awt.Cursor;
import java.awt.Point;
import java.awt.geom.AffineTransform;
import java.awt.geom.Dimension2D;
import java.awt.print.Printable;
import java.awt.print.PrinterJob;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.io.StringReader;
import java.net.URI;
import java.net.URL;
import java.net.URLConnection;
import java.util.List;

import javax.swing.JFileChooser;

import jp.ticketstar.ticketing.printing.gui.AppWindowModel;
import jp.ticketstar.ticketing.printing.gui.IAppWindow;
import jp.ticketstar.ticketing.printing.svg.ExtendedSVG12BridgeContext;
import jp.ticketstar.ticketing.printing.svg.ExtendedSVG12OMDocument;
import jp.ticketstar.ticketing.printing.svg.OurDocumentLoader;
import jp.ticketstar.ticketing.printing.svg.OurSAXSVGDocumentFactory;

import org.apache.batik.bridge.BridgeExtension;
import org.apache.batik.bridge.UserAgent;
import org.apache.batik.dom.svg.SAXSVGDocumentFactory;
import org.apache.batik.gvt.event.EventDispatcher;
import org.apache.batik.gvt.text.Mark;
import org.apache.batik.swing.svg.SVGDocumentLoader;
import org.apache.batik.swing.svg.SVGDocumentLoaderEvent;
import org.apache.batik.swing.svg.SVGDocumentLoaderListener;
import org.apache.batik.swing.svg.SVGUserAgentGUIAdapter;
import org.apache.batik.util.XMLResourceDescriptor;
import org.apache.commons.io.IOUtils;
import org.w3c.dom.Element;
import org.w3c.dom.svg.SVGAElement;
import org.w3c.dom.svg.SVGDocument;

import com.google.gson.Gson;

class PrintQueueList {
	class TicketMetadata {
		Integer id;
	}
	class PrintData {
		String drawing;
	}
	class PrintQueue {
		PrintData data;
	}
	List<TicketMetadata> tickets;
	String svg;
}

interface JsonLoadCallback {
	void success(final int status, final String response);
	void fail(final int status);
}

class JsonLoader extends Thread {
	final String url;
	final JsonLoadCallback callback;
	public JsonLoader(final String url, final JsonLoadCallback callback) {
		this.url = url;
		this.callback = callback;
	}
	
	public void run() {
		try {
			String res = stringOfUrl(url);
			callback.success(200, res);
		} catch (IOException e) {
			e.printStackTrace(System.err);
			callback.fail(0);
			// TODO: logging
		}
	}

	public static String stringOfUrl(String addr) throws IOException {
	    ByteArrayOutputStream output = new ByteArrayOutputStream();
	    URL url = new URL(addr);
	    URLConnection con =  url.openConnection();
	    con.setRequestProperty("Cookie", "backendtkt=0ad7a36b5c172ec198ca55aceebc83a350349138YWRtaW4%3D!userid_type:b64unicode");
	    IOUtils.copy(con.getInputStream(), output);
	    return output.toString();
	}
} 


public class AppService extends SVGUserAgentGUIAdapter implements UserAgent {
	AppWindowModel appWindowModel;
	SVGDocumentLoader documentLoader;
	
	public AppService(AppWindowModel appWindowModel) {
		super(null);
		this.appWindowModel = appWindowModel;
	}

	public void setAppWindow(IAppWindow appWindow) {
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
	
	public void loadFromApi(String apiUrl, String params) {

		final OurDocumentLoader loader = new OurDocumentLoader(this);
		final ExtendedSVG12BridgeContext bridgeContext = new ExtendedSVG12BridgeContext(this, loader);
		
		new JsonLoader(apiUrl, new JsonLoadCallback() {
			public void success(int status, String response) {
				PrintQueueList queueList = (new Gson()).fromJson(response, PrintQueueList.class);
				String uri = "set the document URI, so Batik will be able to resolve relative path";
				SVGDocument doc = null;
				try {
					byte[] bytes = queueList.svg.getBytes("UTF-8");
					InputStream input = new ByteArrayInputStream(bytes);
					OurSAXSVGDocumentFactory documentFactory = new OurSAXSVGDocumentFactory(XMLResourceDescriptor.getXMLParserClassName(), true);
			        doc = documentFactory.createSVGDocument(uri, input);

				} catch (Exception ex) {
					ex.printStackTrace(System.err);
				} finally {
	
				}

				try {
					bridgeContext.setInteractive(false);
					bridgeContext.setDynamic(false);
					appWindowModel.setTicketSetModel(new TicketSetModel(bridgeContext, (ExtendedSVG12OMDocument)doc));
				} catch (Exception e) {
					e.printStackTrace(System.err);
					displayError("Failed to load document\nReason: " + e);
				}
			}
			
			public void fail(int status) {
				System.err.println("Error");
				// TODO Auto-generated method stub	
			}
		}).start();
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
				new AffineTransform(72. / 90, 0, 0, 72. / 90, 0, 0)
			);
			job.setPrintable(printable, appWindowModel.getPageFormat());
			if (job.printDialog())
				job.print();
		} catch (Exception e) {
			displayError("Failed to print tickets\nReason: " + e);
		}
	}
}
