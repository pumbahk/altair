package jp.ticketstar.ticketing.printing.gui;

import java.awt.print.PrinterJob;
import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.io.IOException;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.net.URLConnection;
import java.security.AccessController;
import java.security.PrivilegedAction;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.logging.Logger;

import jp.ticketstar.ticketing.ApplicationException;
import jp.ticketstar.ticketing.LoggingUtils;
import jp.ticketstar.ticketing.PrintableEvent;
import jp.ticketstar.ticketing.PrintableEventListener;
import jp.ticketstar.ticketing.RequestBodySender;
import jp.ticketstar.ticketing.SerializingExecutor;
import jp.ticketstar.ticketing.URLFetcher;
import jp.ticketstar.ticketing.printing.BasicAppService;
import jp.ticketstar.ticketing.printing.Page;
import jp.ticketstar.ticketing.printing.TicketFormat;
import jp.ticketstar.ticketing.printing.TicketPrintable;
import jp.ticketstar.ticketing.printing.URLConnectionSVGDocumentLoader;
import jp.ticketstar.ticketing.svg.ExtendedSVG12BridgeContext;
import jp.ticketstar.ticketing.svg.OurDocumentLoader;
import netscape.javascript.JSObject;

import com.google.gson.stream.JsonWriter;

class AppAppletServiceImpl extends BasicAppService {
	private AppApplet applet;
	private static final Logger logger = Logger.getLogger(BasicAppService.class.getName());
	private AtomicInteger batchUpdate = new AtomicInteger();
	private SerializingExecutor serializingExecutor;
	private volatile boolean ticketDataLoadingNeeded = false;

	protected PropertyChangeListener changeListener = new PropertyChangeListener() {
		public void propertyChange(PropertyChangeEvent evt) {
			if (evt.getNewValue() != null && appWindow != null) {
				ticketDataLoadingNeeded = true;
				if (!applet.config.embedded && batchUpdate.get() == 0)
					doLoadTicketData();
			}
		}
	};

	public void doLoadTicketData() {
		if (!ticketDataLoadingNeeded)
			return;
		invokeWhenDocumentReady(new Runnable() {
			public void run() {
				try {
					final URLConnection conn = applet.newURLConnection(applet.config.peekUrl);
					loadDocument(conn, new RequestBodySender() {
						public String getRequestMethod() {
							return "POST";
						}
						public void send(OutputStream out) throws IOException {
							final JsonWriter writer = new JsonWriter(new OutputStreamWriter(out, "utf-8"));
							writer.beginObject();
							writer.name("ticket_format_id");
							writer.value(((AppAppletModel)model).getTicketFormat().getId());
							writer.name("page_format_id");
							writer.value(model.getPageFormat().getId());
							final Integer orderId = ((AppAppletModel)model).getOrderId();
							if (orderId != null) {
								writer.name("order_id");
								writer.value(orderId);
							}
							writer.endObject();
							writer.flush();
							writer.close();
						}
					});
					ticketDataLoadingNeeded = false;
				} catch (IOException e) {
					throw new ApplicationException(e);
				}
			}
		});
	}

	public void startBatcnUpdate() {
		batchUpdate.incrementAndGet();
	}

	public void endBatchUpdate() {
		if (batchUpdate.decrementAndGet() == 0)
			doLoadTicketData();
	}

	private void notifyPagePrinted(final Page page) {
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
			logger.warning(LoggingUtils.formatException(e));
		}
	}

	private static <V> Callable<V> privileged(final Callable<V> r) {
		return new Callable<V>() {
			@SuppressWarnings("unchecked")
			public V call() throws Exception {
				final Exception[] exceptionThrown = new Exception[1];
				final V retval = (V)AccessController.doPrivileged(new PrivilegedAction<Object>() {
					public Object run() {
						try {
							return r.call();
						} catch (Exception e) {
							exceptionThrown[0] = e;
						}
						return null;
					}
				});
				if (exceptionThrown[0] != null)
					throw exceptionThrown[0];
				return retval;
			}
		};
	}

	public void printAll() {
		logger.entering(this.getClass().getName(), "printAll");
		if (applet.config.embedded)
			doLoadTicketData();
		invokeWhenDocumentReady(new Runnable() {
			public void run() {
				try {
					serializingExecutor.executeSynchronously(privileged(new Callable<Void>() {
						public Void call() throws Exception {
							model.setPrintingStatus(Boolean.TRUE);
							try {
								final PrinterJob job = PrinterJob.getPrinterJob();
								job.setPrintService(model.getPrintService());
								final TicketPrintable printable = createTicketPrintable(job);
								printable.addPrintableEventListener(new PrintableEventListener() {
									public void pagePrinted(PrintableEvent evt) {
										final Page page = printable.getPages().get(evt.getPageIndex());
										serializingExecutor.execute(new Runnable() {
											public void run() {
												notifyPagePrinted(page);
											}
										});
										model.getPageSetModel().getPages().remove(page);
									}
								});
								job.setPrintable(printable, model.getPageFormat());
								job.print();
							} finally {
								model.setPrintingStatus(Boolean.FALSE);
							}
							return null;
						}
					}));
				} catch (Exception e) {
					logger.warning(LoggingUtils.formatException(e));
					displayError("Failed to print tickets\nReason: " + e);
				}
			}
		});
		logger.exiting(this.getClass().getName(),  "printAll");
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

	public AppApplet getApplet() {
		return applet;
	}

	public void invokeWhenDocumentReady(final Runnable runnable) {
		serializingExecutor.execute(new Runnable() {
			public void run() {
				AppAppletServiceImpl.super.invokeWhenDocumentReady(runnable);
			}
		});
	}

	protected void unbind() {
		model.removePropertyChangeListener(changeListener);
		model.removePropertyChangeListener(changeListener);
		model.removePropertyChangeListener(changeListener);
	}
	
	protected void bind() {
		model.addPropertyChangeListener("pageFormat", changeListener);
		model.addPropertyChangeListener("ticketFormat", changeListener);
		model.addPropertyChangeListener("orderId", changeListener);
	}

	public AppAppletServiceImpl(AppApplet applet, AppAppletModel model) {
		super(model);
		this.applet = applet;
		this.serializingExecutor = new SerializingExecutor(applet);
		this.serializingExecutor.start();
		bind();
	}
}