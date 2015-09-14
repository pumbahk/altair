package jp.ticketstar.ticketing.printing.gui;

import java.awt.print.PrinterJob;
import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.io.IOException;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.net.URLConnection;
import java.security.AccessController;
import java.security.PrivilegedExceptionAction;
import java.util.ArrayList;
import java.util.List;
import java.util.Queue;
import java.util.LinkedList;
import java.util.concurrent.Future;
import java.util.concurrent.RunnableFuture;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.logging.Level;
import java.util.logging.Logger;

import jp.ticketstar.ticketing.ApplicationException;
import jp.ticketstar.ticketing.LoggingUtils;
import jp.ticketstar.ticketing.PrintableEvent;
import jp.ticketstar.ticketing.PrintableEventListener;
import jp.ticketstar.ticketing.RequestBodySender;
import jp.ticketstar.ticketing.SerializingExecutor;
import jp.ticketstar.ticketing.URLFetcher;
import jp.ticketstar.ticketing.printing.BasicAppService;
import jp.ticketstar.ticketing.printing.OurPageFormat;
import jp.ticketstar.ticketing.printing.Page;
import jp.ticketstar.ticketing.printing.PageEvent;
import jp.ticketstar.ticketing.printing.TicketFormat;
import jp.ticketstar.ticketing.printing.TicketPrintable;
import jp.ticketstar.ticketing.printing.URLConnectionSVGDocumentLoader;
import jp.ticketstar.ticketing.svg.ExtendedSVG12BridgeContext;
import jp.ticketstar.ticketing.svg.ExtendedSVG12OMDocument;
import jp.ticketstar.ticketing.svg.OurDocumentLoader;
import netscape.javascript.JSObject;

import com.google.gson.stream.JsonWriter;

class AppAppletServiceImpl extends BasicAppService {
    private AppApplet applet;
    private static final Logger logger = Logger.getLogger(BasicAppService.class.getName());
    private AtomicInteger batchUpdate = new AtomicInteger();
    private SerializingExecutor serializingExecutor;
    private volatile boolean ticketDataLoadingNeeded = false;
    private Queue<String> dequeuingRequestQueue;
    private RunnableFuture<?> bundlerTask;

    protected PropertyChangeListener changeListener = new PropertyChangeListener() {
        public void propertyChange(PropertyChangeEvent evt) {
            if (evt.getNewValue() != null && appWindow != null) {
                logger.finer("property " + evt.getPropertyName() + " changed to " + evt.getNewValue());
                ticketDataLoadingNeeded = true;
                if (!applet.config.embedded && batchUpdate.get() == 0)
                    doLoadTicketData(null);
            }
        }
    };
    
    private void dumpPageSetModel() {
        if (logger.isLoggable(java.util.logging.Level.FINER)) {
            for (Page page: model.getPageSetModel().getPages()) {
                StringBuffer buf = new StringBuffer();
                buf.append("page ");
                buf.append(page.getName());
                buf.append(": ");
                boolean first = true;
                for (String queueId: page.getQueueIds()) {
                    if (!first) {
                        buf.append(", ");
                    }
                    buf.append(queueId);
                }
                first = false;
                logger.finer(buf.toString());
            }
            logger.finer(model.getPageSetModel().getPages().size() + " pages total");
        }
    }
    
    private Future<ExtendedSVG12OMDocument> loadDocument(final String orderId, final TicketFormat ticketFormat, final OurPageFormat pageFormat, final List<String> queueIds) throws IOException {
        final URLConnection conn = applet.newURLConnection(applet.config.peekUrl);
        return loadDocument(conn, new RequestBodySender() {
            public String getRequestMethod() {
                return "POST";
            }

            public void send(OutputStream out) throws IOException {
                logger.entering(this.getClass().getName() + " loadDocument", "send");
                try {
                    final JsonWriter writer = new JsonWriter(new OutputStreamWriter(out, "utf-8"));
                    writer.beginObject();
                    writer.name("ticket_format_id");
                    writer.value(ticketFormat.getId());
                    writer.name("page_format_id");
                    writer.value(pageFormat.getId());
                    if (orderId != null) {
                        writer.name("order_id");
                        writer.value(orderId);
                    }
                    if (queueIds != null) {
                        writer.name("queue_ids");
                        writer.beginArray();
                        for (String queueId: queueIds) {
                            writer.value(queueId);
                        }
                        writer.endArray();
                    }
                    writer.endObject();
                    writer.flush();
                    writer.close();
                } finally {
                    logger.exiting(this.getClass().getName() + " loadDocument", "send");
                }
            }
        });
    }

    public void doLoadTicketData(final Runnable continuation) {
        logger.entering(this.getClass().getName(), "doLoadTicketData");
        if (!ticketDataLoadingNeeded) {
            logger.finer("data seems to have been loaded already");
            logger.finer("continuation=" + continuation);
            if (continuation != null)
                invokeWhenDocumentReady(continuation, serializingExecutor);
            return;
        }
        final String orderId = ((AppAppletModel)model).getOrderId();
        final TicketFormat ticketFormat = ((AppAppletModel)model).getTicketFormat();
        final OurPageFormat pageFormat = model.getPageFormat();
        final List<String> queueIds = ((AppAppletModel)model).getQueueIds();
        invokeWhenDocumentReady(new Runnable() {
            @Override
            public String toString() {
                return "doLoadTicketData";
            }

            @Override
            public void run() {
                logger.entering(this.getClass().getName() + " (doLoadTicketData)", "run");
                try {
                    ticketDataLoadingNeeded = false;
                    loadDocument(orderId, ticketFormat, pageFormat, queueIds).get();
                    if (continuation != null)
                        continuation.run();
                } catch (Exception e) {
                    throw new ApplicationException(e);
                } finally {
                    logger.exiting(this.getClass().getName() + " (doLoadTicketData)", "run");
                }
            }
        }, serializingExecutor);
        logger.exiting(this.getClass().getName(), "doLoadTicketData");
    }

    public void startBatcnUpdate() {
        logger.finer("startBatchUpdate");
        batchUpdate.incrementAndGet();
    }

    public void endBatchUpdate() {
        logger.finer("endBatchUpdate");
        if (batchUpdate.decrementAndGet() == 0)
            doLoadTicketData(null);
    }

    private void notifyPagePrinted(final Page page) {
        synchronized (dequeuingRequestQueue) {
            dequeuingRequestQueue.addAll(page.getQueueIds());
        }
    }

    public void printAll() {
        logger.entering(this.getClass().getName(), "printAll");
        doLoadTicketData(new Runnable() {
            @Override
            public String toString() {
                return "printAll";
            }

            @Override
            public void run() {
                logger.entering(this.getClass().getName() + " (printAll)", "run");
                dumpPageSetModel();
                logger.finer("printingStatus set to TRUE");
                model.setPrintingStatus(Boolean.TRUE);
                try {
                    AccessController.doPrivileged(new PrivilegedExceptionAction<Void>() {
                        @Override
                        public Void run() throws Exception {
                            final PrinterJob job = PrinterJob.getPrinterJob();
                            job.setPrintService(model.getPrintService());
                            final TicketPrintable printable = createTicketPrintable(job);
                            printable.addPrintableEventListener(new PrintableEventListener() {
                                public void pagePrinted(PrintableEvent evt) {
                                    final Page page = printable.getPages().get(evt.getPageIndex());
                                    if (logger.isLoggable(Level.FINER)) {
                                        StringBuffer buf = new StringBuffer();
                                        buf.append("pagePrinted: page [");
                                        buf.append(page.getName());
                                        buf.append("]: ");
                                        boolean first = true;
                                        for (String queueId: page.getQueueIds()) {
                                            if (!first) {
                                                buf.append(", ");
                                            }
                                            buf.append(queueId);
                                        }
                                        first = false;
                                        logger.finer(buf.toString());
                                    }
                                    notifyPagePrinted(page);
                                    firePagePrintedEvent(new PageEvent(this, page));
                                    model.getPageSetModel().getPages().remove(page);
                                    dumpPageSetModel();
                                }
                            });    
                            job.setPrintable(printable, model.getPageFormat());
                            job.print();
                            return null;
                        }
                    });
                } catch (Exception e) {
                    logger.warning(LoggingUtils.formatException(e));
                    displayError("Failed to print tickets\nReason: " + e);
                } finally {
                    logger.finer("printingStatus set to FALSE");
                    model.setPrintingStatus(Boolean.FALSE);
                }
                logger.exiting(this.getClass().getName() + " (printAll)", "run");
            }
        });
        logger.exiting(this.getClass().getName(),  "printAll");
    }

    public synchronized Future<ExtendedSVG12OMDocument> loadDocument(URLConnection conn, RequestBodySender sender) {
        logger.entering(this.getClass().getName(), "loadDocument");
        try {
            if (this.documentLoader != null) {
                logger.severe("document is being loaded");
                throw new IllegalStateException("document is being loaded");
            }
            final OurDocumentLoader loader = new OurDocumentLoader(this);
            final URLConnectionSVGDocumentLoader documentLoader = new URLConnectionSVGDocumentLoader(conn, sender, loader);
            this.documentLoader = documentLoader;
            LoaderListener<ExtendedSVG12OMDocument> listener = new LoaderListener<ExtendedSVG12OMDocument>(new ExtendedSVG12BridgeContext(this, loader));
            documentLoader.addSVGDocumentLoaderListener(listener);
            documentLoader.start();
            return listener;
        } finally {
            logger.exiting(this.getClass().getName(), "loadDocument");
        }
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
        logger.entering(this.getClass().getName(), "setTicketFormat");
        ((AppAppletModel)model).setTicketFormat(ticketFormat);
        logger.exiting(this.getClass().getName(), "setTicketFormat");
    }

    public void addListenerForTicketFormat(PropertyChangeListener listener) {
       ((AppAppletModel)model).addPropertyChangeListener("ticketFormat", listener);
    }

    public void filterByOrderId(String orderId) {
        logger.entering(this.getClass().getName(), "filterByOrderId");
        ((AppAppletModel)model).setOrderId(orderId);
        logger.exiting(this.getClass().getName(), "filterByOrderId");
    }

    public void filterByQueueIds(List<String> queueIds) {
        logger.entering(this.getClass().getName(), "filterByQueueIds");
        if (logger.isLoggable(java.util.logging.Level.FINER)) {
            StringBuffer buf = new StringBuffer();
            boolean first = true;
            for (String queueId: queueIds) {
                if (!first) {
                    buf.append(", ");
                }
                buf.append(queueId);
                first = false;
            }
            logger.finer(buf.toString());
        }
        ((AppAppletModel)model).setQueueIds(queueIds);
        logger.exiting(this.getClass().getName(), "filterByQueueIds");
    }

    public AppApplet getApplet() {
        return applet;
    }

    protected void unbind() {
        model.removePropertyChangeListener("pageFormat", changeListener);
        model.removePropertyChangeListener("ticketFormat", changeListener);
        model.removePropertyChangeListener("orderId", changeListener);
        model.removePropertyChangeListener("queueIds", changeListener);
    }
    
    protected void bind() {
        model.addPropertyChangeListener("pageFormat", changeListener);
        model.addPropertyChangeListener("ticketFormat", changeListener);
        model.addPropertyChangeListener("orderId", changeListener);
        model.addPropertyChangeListener("queueIds", changeListener);
    }

    public void dispose() {
        bundlerTask.cancel(false);
        serializingExecutor.terminate();
    }

    public AppAppletServiceImpl(final AppApplet applet, AppAppletModel model) {
        super(model);
        this.applet = applet;
        this.serializingExecutor = new SerializingExecutor(applet);
        this.dequeuingRequestQueue = new LinkedList<String>();
        this.bundlerTask = new PeriodicBundleSubmitter<String>(
            new QueueBundler<String>(this.dequeuingRequestQueue, 100),
            new PeriodicBundleSubmitter.BundleHandler<String>() {
                @Override
                public void handle(final List<String> bundle) {
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
                                for (final String queueId: bundle)
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
            },
            500
        ).yield();
        applet.newThread(this.bundlerTask).start();
        this.serializingExecutor.start();
        bind();
    }
}
