package jp.ticketstar.ticketing.printing.gui;

import java.io.IOException;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.net.URLConnection;
import java.awt.print.PrinterJob;
import java.beans.PropertyChangeListener;
import java.security.AccessController;
import java.security.PrivilegedAction;
import java.util.ArrayList;
import java.util.List;

import jp.ticketstar.ticketing.printing.BasicAppService;
import jp.ticketstar.ticketing.printing.Page;
import jp.ticketstar.ticketing.printing.PrintableEvent;
import jp.ticketstar.ticketing.printing.PrintableEventListener;
import jp.ticketstar.ticketing.printing.RequestBodySender;
import jp.ticketstar.ticketing.printing.StandardAppService;
import jp.ticketstar.ticketing.printing.TicketFormat;
import jp.ticketstar.ticketing.printing.TicketPrintable;
import jp.ticketstar.ticketing.printing.URLConnectionSVGDocumentLoader;
import jp.ticketstar.ticketing.printing.URLFetcher;
import jp.ticketstar.ticketing.printing.svg.ExtendedSVG12BridgeContext;
import jp.ticketstar.ticketing.printing.svg.OurDocumentLoader;

import netscape.javascript.JSObject;

import com.google.gson.stream.JsonWriter;

public class AppAppletService extends BasicAppService implements StandardAppService {
	private AppApplet applet;
	
	public AppAppletService(AppApplet applet, AppAppletModel model) {
		super(model);
		this.applet = applet;
	}

	public synchronized void loadDocument(URLConnection conn, RequestBodySender sender) {
		if (this.documentLoader != null)
			return;
		final OurDocumentLoader loader = new OurDocumentLoader(this);
		final URLConnectionSVGDocumentLoader documentLoader = new URLConnectionSVGDocumentLoader(conn, sender, loader);
		this.documentLoader = documentLoader;
		documentLoader.addSVGDocumentLoaderListener(new LoaderListener(new ExtendedSVG12BridgeContext(this, loader)));
		documentLoader.start();
	}
	
	@Override
	public void printAll() {
		AccessController.doPrivileged(new PrivilegedAction<Object>() {
			public Object run() {
				try {
					final PrinterJob job = PrinterJob.getPrinterJob();
					job.setPrintService(model.getPrintService());
					final TicketPrintable printable = createTicketPrintable(job);
					printable.addPrintableEventListener(new PrintableEventListener() {
						public void pagePrinted(PrintableEvent evt) {
							final Page page = printable.getPages().get(evt.getPageIndex());

							try {
								URLFetcher.fetch(applet.newURLConnection(applet.config.dequeueUrl), new RequestBodySender() {
									public String getRequestMethod() {
										return "POST";
									}
	
									@Override
									public void send(OutputStream out) throws IOException {
										final JsonWriter writer = new JsonWriter(new OutputStreamWriter(out, "utf-8"));
										writer.beginObject();
										writer.name("queue_ids");
										writer.beginArray();
										for (final String queueId: page.getQueueIds())
											writer.value(queueId);
										writer.endArray();
										writer.endObject();
										writer.flush();
										writer.close();
									}
								});
							} catch (IOException e) {
								displayError(e);
							}
							model.getPageSetModel().getPages().remove(page);
						}
					});
					job.setPrintable(printable, model.getPageFormat());
					job.print();
				} catch (Exception e) {
					e.printStackTrace();
					displayError("Failed to print tickets\nReason: " + e);
				}
				return null;
			}
		});
	}

    public void displayError(String message) {
    	final JSObject window = JSObject.getWindow(applet);
    	window.call("alert", new Object[] { message });
    }

    /**
     * Displays an error resulting from the specified Exception.
     */
    public void displayError(Exception ex) {
    	ex.printStackTrace();
    }

    /**
     * Displays a message in the User Agent interface.
     * The given message is typically displayed in a status bar.
     */
    public void displayMessage(String message) {
        // Can't do anything don't have a status bar...
    }

	public List<TicketFormat> getTicketFormats() {
		List<TicketFormat> ticketFormats = ((AppAppletModel)model).getTicketFormats();
		return ticketFormats == null ? null: new ArrayList<TicketFormat>(ticketFormats);
	}

	public TicketFormat getTicketFormat() {
		return ((AppAppletModel)model).getTicketFormat();
	}
	
	public void setTicketFormat(TicketFormat ticketFormat) {
		((AppAppletModel)model).setTicketFormat(ticketFormat);
	}

	public void filterByOrderId(Integer orderId) {
		((AppAppletModel)model).setOrderId(orderId);
	}

	public void addListenerForTicketFormat(PropertyChangeListener listener) {
		((AppAppletModel)model).addPropertyChangeListener("ticketFormat", listener);
	}
}