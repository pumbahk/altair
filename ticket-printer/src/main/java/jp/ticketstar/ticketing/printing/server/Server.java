package jp.ticketstar.ticketing.printing.server;

import java.awt.AWTException;
import java.awt.Dimension;
import java.awt.Image;
import java.awt.MenuItem;
import java.awt.PopupMenu;
import java.awt.SystemTray;
import java.awt.TrayIcon;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.geom.AffineTransform;
import java.awt.print.PrinterException;
import java.awt.print.PrinterJob;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.io.Reader;
import java.io.UnsupportedEncodingException;
import java.net.HttpURLConnection;
import java.net.InetSocketAddress;
import java.net.URI;
import java.net.URISyntaxException;
import java.net.URL;
import java.net.URLConnection;
import java.net.URLDecoder;
import java.nio.charset.Charset;
import java.security.AccessController;
import java.security.PrivilegedAction;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ThreadFactory;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.logging.Level;
import java.util.logging.LogRecord;
import java.util.logging.Logger;
import java.util.logging.SimpleFormatter;

import javax.imageio.ImageIO;
import javax.print.PrintService;
import javax.swing.JFrame;
import javax.swing.JScrollPane;
import javax.swing.JTextArea;
import javax.swing.text.BadLocationException;

import jp.ticketstar.ticketing.DeferredValue;
import jp.ticketstar.ticketing.RequestBodySender;
import jp.ticketstar.ticketing.printing.OurPageFormat;
import jp.ticketstar.ticketing.printing.Page;
import jp.ticketstar.ticketing.printing.PageElementIterator;
import jp.ticketstar.ticketing.printing.PageSetModel;
import jp.ticketstar.ticketing.printing.TicketPrintable;
import jp.ticketstar.ticketing.printing.URLConnectionSVGDocumentLoader;
import jp.ticketstar.ticketing.printing.gui.AppWindowService;
import jp.ticketstar.ticketing.printing.gui.FormatLoader;
import jp.ticketstar.ticketing.svg.ExtendedSVG12BridgeContext;
import jp.ticketstar.ticketing.svg.ExtendedSVG12OMDocument;
import jp.ticketstar.ticketing.svg.OurDocumentLoader;
import jp.ticketstar.ticketing.svg.SVGOMPageElement;

import org.apache.batik.dom.svg.SVGOMElement;
import org.apache.batik.dom.svg.SVGOMTitleElement;
import org.apache.batik.swing.svg.SVGDocumentLoader;
import org.apache.batik.swing.svg.SVGDocumentLoaderEvent;
import org.apache.batik.swing.svg.SVGDocumentLoaderListener;
import org.w3c.dom.Node;

import com.google.common.base.Joiner;
import com.google.common.base.Optional;
import com.google.common.net.InetAddresses;
import com.google.common.net.MediaType;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonIOException;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.google.gson.JsonSyntaxException;
import com.google.gson.stream.JsonWriter;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.Headers;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;

@SuppressWarnings("restriction")
class LogWindow extends JFrame {
    private static final long serialVersionUID = 1L;
    int maxLines = 500;
    JTextArea textArea;
    JScrollPane outer;
    public LogWindow() {
        super("Log window");
        initialize();
    }

    public void appendLine(String l) {
        int lineCount = textArea.getLineCount();
        if (lineCount >= maxLines) {
            try {
                textArea.replaceRange("", 0, textArea.getLineStartOffset(lineCount - maxLines + 1));
            } catch (BadLocationException e) {
            }
        }
        try {
            textArea.setCaretPosition(textArea.getLineEndOffset(lineCount - 1));
        } catch (BadLocationException e) {
        }
        textArea.append(l);
    }

    protected void initialize() {
        textArea = new JTextArea();
        textArea.setEditable(false);
        outer = new JScrollPane(textArea);
        outer.setPreferredSize(new Dimension(400, 400));
        setContentPane(outer);
        pack();
    }
}

class Job extends DeferredValue<Exception> {
    Integer id;
    Date createdAt;

    String printer;
    OurPageFormat pageFormat;
    String svg;
    
    String peekUrl;
    String dequeueUrl;
    String cookie;
    int pageFormatId;
    int ticketFormatId;
    
    // orderIdかqueueIdsのいずれか片方を受け取る
    // orderIdを受け取った場合は、peekして得たsvgの中にqueueIdsが埋めこまれている
    List<Integer> queueIds;
    Integer orderId;
    
    PageSetModel pageSet;

    public void dispose() {
        // these are leaky
        svg = null;
        pageSet = null;
        pageFormat = null;
        peekUrl = null;
        dequeueUrl = null;
        cookie = null;
    }

    public void disposeAndSet(Exception e) {
        dispose();
        set(e);
    }

    @Override
    public String toString() {
        return String.format(
            "Job(id=%s, peekUrl=%s, dequeueUrl=%s, cookie=%s, pageFormatId=%d, ticketFormatId=%d, orderId=%d, queueIds=%s)",
            id,
            peekUrl,
            dequeueUrl,
            cookie,
            pageFormatId,
            ticketFormatId,
            orderId,
            Joiner.on(".").join(queueIds)
        );
    }
}

class Request {
    public static final class KeyValuePair {
        private String key;
        private String value;

        public String getKey() {
            return key;
        }

        public String getValue() {
            return value;
        }

        public KeyValuePair(String key, String value) {
            this.key = key;
            this.value = value;
        }
    }

    public static final class Params extends ArrayList<KeyValuePair> {
        private static final long serialVersionUID = 1L;

        public List<String> getList(String key) {
            final List<String> retval = new ArrayList<String>(size());
            for (final KeyValuePair kv: this) { 
                if (kv.getKey().equals(key)) {
                    retval.add(kv.getValue());
                }
            }
            return retval;
        }

        public String getFirst(String key) {
            List<String> values = getList(key);
            if (values.size() == 0)
                return null;
            return values.get(0);
        }
    }

    @SuppressWarnings("restriction")
    protected HttpExchange exchange;
    protected Params params;
    protected String requestURIEncoding;
    protected Optional<MediaType> contentType;

    @SuppressWarnings("restriction")
    public Request(final HttpExchange exchange, final String requestURIEncoding) {
        this.exchange = exchange;
        this.params = null;
        this.requestURIEncoding = requestURIEncoding;
    }

    @SuppressWarnings("restriction")
    public String getMethod() {
        return exchange.getRequestMethod();
    }
    
    @SuppressWarnings("restriction")
    public Headers getHeaders() {
        return exchange.getRequestHeaders();
    }

    @SuppressWarnings("restriction")
    public InputStream getBodyInputStream() {
        return exchange.getRequestBody();
    }

    public Reader getBodyReader() {
        final Optional<MediaType> contentType = getContentType();
        final Charset charset = contentType.or(MediaType.OCTET_STREAM).charset().or(Server.UTF_8_CHARSET);
        return new InputStreamReader(getBodyInputStream(), charset);
    }
    
    public Params getParams() {
        if (this.params == null) {
            final Params params = new Params();
            @SuppressWarnings("restriction")
            final String query = exchange.getRequestURI().getRawQuery();
            if (query != null) {
                try {
                    for (final String c: query.split("&")) {
                        String[] kv = c.split("=", 2);
                        if (kv.length == 1) {
                            params.add(new KeyValuePair(URLDecoder.decode(kv[0], requestURIEncoding), null));
                        } else {
                            params.add(new KeyValuePair(URLDecoder.decode(kv[0], requestURIEncoding), URLDecoder.decode(kv[1], requestURIEncoding)));
                        }
                    }
                } catch (UnsupportedEncodingException e) {
                    throw new RuntimeException(e);
                }
            }
            this.params = params;
        }
        return this.params;
    }

    @SuppressWarnings("restriction")
    public boolean getJsonAcception() {
        List<String> as_ = getParams().getList("as");
        if (as_.size() > 0 && as_.get(0) == "json")
            return true;
        
        List<String> accepts = getHeaders().get("Accept");
        if(accepts != null) {
            for(String accept: accepts) {
                for(String type: accept.split(",")) {
                    if(type.endsWith("javascript") || type.endsWith("json")) {
                        return true;
                    } else if(type.endsWith("html")) {
                        return false;
                    }
                }
            }
        }
        return false;
    }

    @SuppressWarnings("restriction")
    public Optional<MediaType> getContentType() {
        if (this.contentType == null) {
            final String contentTypeStr = exchange.getRequestHeaders().getFirst("Content-Type");
            if (contentTypeStr != null)
                this.contentType = Optional.<MediaType>of(MediaType.parse(contentTypeStr));
            else
                this.contentType = Optional.<MediaType>absent();
        }
        return this.contentType;
    }

    @SuppressWarnings("restriction")
    public String getOrigin() {
        return exchange.getRequestHeaders().getFirst("Origin");
    }
}

@SuppressWarnings("restriction")
public class Server {
    private static final Logger log = Logger.getLogger(Server.class.getName());
    private static final Pattern addrRegex = Pattern.compile("^(?:\\[([^]]+)\\]|([^:]*)):([0-9]+)");
    public static final Charset UTF_8_CHARSET = Charset.forName("UTF-8");

    private AppWindowService service;
    
    private InetSocketAddress address;
    
    private List<URI> originHosts = new ArrayList<URI>();
    
    private int nextId;
    private BlockingQueue<Job> queue;
    private long gcInterval;

    private ThreadFactory threadFactory = Executors.defaultThreadFactory();
    
    private Thread printThread;
    private AtomicBoolean printThreadIsRunning = new AtomicBoolean(false);

    private Thread gcThread;
    private AtomicBoolean gcThreadIsRunning = new AtomicBoolean(false);
    
    private TrayIcon icon;
    private MenuItem statusLabel;
    
    private Charset jsonCharset = UTF_8_CHARSET;
    private HttpServer httpServer;

    private CountDownLatch disposed = new CountDownLatch(3);
    
    private LogWindow logWindow;

    private Map<Integer, Job> jobsBeingProcessed = new HashMap<Integer, Job>();

    private static class HandlerException extends Exception {
        private static final long serialVersionUID = 1L;
        private int status = 500;

        public int getStatus() {
            return status;
        }

        public HandlerException(String message, Throwable cause, int status) {
            super(message, cause);
            this.status = status;
        }

        public HandlerException(String message, int status) {
            super(message);
            this.status = status;
        }
    }
    
    private class Handler implements HttpHandler {
        private final GsonBuilder gsonBuilder = new GsonBuilder().setPrettyPrinting();

        private Gson getGson() {
            return gsonBuilder.create();
        }

        private Charset setUpResponse(Request request, HttpExchange exchange, MediaType type) {
            Optional<Charset> charset = type.charset();
            Headers responseHeaders = exchange.getResponseHeaders();
            responseHeaders.add("Content-Type", type.toString());
            final String origin = request.getOrigin();
            if (origin != null) {
                try {
                    final URI givenOrigin = new URI(origin);
                    boolean matched = false;
                    for (final URI originHost: originHosts) {
                        final URI result = originHost.relativize(givenOrigin);
                        if (result.getScheme() == null && result.getHost() == null && result.getPort() == -1 && result.getUserInfo() == null) {
                            matched = true;
                            exchange.getResponseHeaders().add("Access-Control-Allow-Origin", origin);
                        }
                    }
                    if (!matched) {
                        log.warning("Origin " + origin + " is not included in the allowed origin list: " + Joiner.on(", ").join(originHosts));
                    }
                } catch (URISyntaxException e) {
                    log.log(Level.INFO, "WTF?", e);
                }
            }
            responseHeaders.add("Access-Control-Request-Method", "GET, POST, OPTIONS");
            responseHeaders.add("Access-Control-Allow-Headers", "Accept,Content-Type");
            responseHeaders.add("Connection", "close");
            responseHeaders.add("Cache-Control", "no-cache");
            return charset.or(UTF_8_CHARSET);
        }

        private Map<String, Object> handlePrinters(Request request, HttpExchange exchange) throws HandlerException {
            final Map<String,Object> data = new HashMap<String,Object>();
            List<String> list = new ArrayList<String>();
            for(PrintService ps: getPrintServices()) {
                list.add(ps.getName());
            }
            data.put("printers", list);
            return data;
        }

        private Map<String, Object> handleQueue(Request request, HttpExchange exchange) throws HandlerException {
            Job[] jobs;
            synchronized (queue) {
                jobs = new Job[queue.size()];
                queue.toArray(jobs);
            }
            List<String> list = new ArrayList<String>();
            for (Job job: jobs) {
                list.add("job-" + job.id);
            }
            Map<String,Object> data = new HashMap<String,Object>();
            data.put("jobs", list);
            return data;
        }

        private String pickStringFromJsonObject(JsonObject obj, String key) throws HandlerException {
            final JsonElement value = obj.get(key);
            if (value == null) {
                throw new HandlerException(String.format("required parameter \"%s\" is missing", key), 400);
            }
            try {
                return value.getAsString();
            } catch (Exception e) {
                throw new HandlerException(String.format("required parameter \"%s\" is invalid", key), 400);
            }
        }

        private JsonObject pickObjectFromJsonObject(JsonObject obj, String key) throws HandlerException {
            final JsonElement value = obj.get(key);
            if (value == null) {
                throw new HandlerException(String.format("required parameter \"%s\" is missing", key), 400);
            }
            try {
                return value.getAsJsonObject();
            } catch (Exception e) {
                throw new HandlerException(String.format("required parameter \"%s\" is invalid", key), 400);
            }
        }

        private JsonArray pickArrayFromJsonObject(JsonObject obj, String key) throws HandlerException {
            final JsonElement value = obj.get(key);
            if (value == null) {
                throw new HandlerException(String.format("required parameter \"%s\" is missing", key), 400);
            }
            try {
                return value.getAsJsonArray();
            } catch (Exception e) {
                throw new HandlerException(String.format("required parameter \"%s\" is invalid", key), 400);
            }
        }
 
        private int pickIntFromJsonObject(JsonObject obj, String key) throws HandlerException {
            final JsonElement value = obj.get(key);
            if (value == null) {
                throw new HandlerException(String.format("required parameter \"%s\" is missing", key), 400);
            }
            try {
                return value.getAsInt();
            } catch (Exception e) {
                throw new HandlerException(String.format("required parameter \"%s\" is invalid", key), 400);
            }
        }
 
        private Job jobFromJsonObject(JsonObject obj) throws HandlerException {
            final Job job = new Job();
            job.createdAt = new Date(); 
            job.printer = pickStringFromJsonObject(obj, "printer");
            job.pageFormat = FormatLoader.buildPageFormat(pickObjectFromJsonObject(obj, "page"));
            job.peekUrl = pickStringFromJsonObject(obj, "peek_url");
            job.dequeueUrl = pickStringFromJsonObject(obj, "dequeue_url");
            job.cookie = pickStringFromJsonObject(obj, "cookie");
            job.pageFormatId = pickIntFromJsonObject(obj, "page_format_id");
            job.ticketFormatId = pickIntFromJsonObject(obj, "ticket_format_id");
            if(obj.has("order_id")) {
                job.orderId = pickIntFromJsonObject(obj, "order_id");
                job.queueIds = null;
                job.svg = null;
            } else if(obj.has("queue_ids")) {
                final JsonArray queueIds = pickArrayFromJsonObject(obj, "queue_ids");
                job.queueIds = new ArrayList<Integer>(queueIds.size());
                for (int i = 0; i < queueIds.size(); i++) {
                    job.queueIds.add(queueIds.get(i).getAsInt());
                }
                job.orderId = null;
                job.svg = null;
            } else if(obj.has("svg")) {
                job.orderId = null;
                job.queueIds = null;
                job.svg = pickStringFromJsonObject(obj, "svg");
            } else {
                throw new HandlerException("Invalid request", 400);
            }
            return job;
        }

        private Map<String, Object> handleProcess(Request request, HttpExchange exchange) throws HandlerException {
            if (!request.getMethod().equals("POST")) {
                throw new HandlerException("bad request method", 400);
            }
                                // リクエストをオブジェクトとして読み込む
            log.info("Building request");
            Reader reader = request.getBodyReader();
            JsonObject obj = null;
            try {
                try {
                    obj = new JsonParser().parse(reader).getAsJsonObject();
                } finally {
                    reader.close();
                }
            } catch (IOException e) {
                throw new HandlerException("error parsing response", 400);
            } catch (JsonSyntaxException e) {
                throw new HandlerException("error parsing response", 400);
            } catch (JsonIOException e) {
                throw new HandlerException("error parsing response", 400);
            }
            final Job job = jobFromJsonObject(obj);
            log.info("Processing...");
            try {
                processRequest(job);
            } catch (IOException e) {
                throw new HandlerException("internal server error", e, 500);
            }
            Map<String,Object> data = new HashMap<String,Object>();
            data.put("job_id", Integer.toString(job.id));
            data.put("poll_url", buildPollUrl(request, job));
            return data;
        }

        private Map<String, Object> handlePoll(Request request, HttpExchange exchange, String jobIdStr) throws HandlerException {            
            if (!request.getMethod().equals("GET")) {
                throw new HandlerException("bad request method", 400);
            }
            final String timeoutStr = request.getParams().getFirst("timeout");
            int jobId = 0;
            try {
                jobId = Integer.parseInt(jobIdStr);
            } catch (NumberFormatException e) {
                throw new HandlerException("bad job_id", e, 400);
            }
            Integer timeout = null;
            if (timeoutStr != null) {
                try {
                    timeout = Integer.valueOf(timeoutStr);
                } catch (NumberFormatException e) {
                    throw new HandlerException("bad timeout value", e, 400);
                }
            }
            Job job = null;
            synchronized (jobsBeingProcessed) {
                job = jobsBeingProcessed.get(jobId);
            }
            if (job == null) {
                throw new HandlerException(String.format("no such Job(id=%d)", jobId), 404);
            }
            Map<String,Object> data = new HashMap<String,Object>();
            Exception result;
            try {
                result = timeout != null ? job.get(timeout.longValue(), TimeUnit.MILLISECONDS): job.get();
                synchronized (jobsBeingProcessed) {
                    jobsBeingProcessed.remove(jobId);
                }
                if (result != null) {
                    data.put("error_class", result.getClass().getName()); 
                    data.put("error_message", result.getMessage()); 
                } else {
                    data.put("error_class", null);
                    data.put("error_message", null);
                }
            } catch (InterruptedException e) {
                throw new HandlerException("interrupted", 500);                
            } catch (TimeoutException e) {
                data.put("status", "timeout");
            }
            return data;
        }
 
        private String buildPollUrl(Request request, Job job) {
            return String.format("/poll/%d", job.id);
        }

        @Override
        public void handle(HttpExchange exchange) throws IOException {
            try {
                final Request request = new Request(exchange, "UTF-8");
                                            // クライアントとリクエストを表示する
                log.info("new connection from " + exchange.getRemoteAddress().toString() + " with request " + exchange.getRequestMethod() + " " + exchange.getRequestURI());
                String path = exchange.getRequestURI().getPath();
                Map<String, Object> retval = null;
                HandlerException exc = null;
    
                // routing
                if (request.getMethod().equals("OPTIONS")) {
                    setUpResponse(request, exchange, MediaType.PLAIN_TEXT_UTF_8);
                    exchange.sendResponseHeaders(200, 0);
                    exchange.getResponseBody().close();
                } else {
                    try {
                        if (path.equals("/printers")) {
                            retval = handlePrinters(request, exchange);
                        } else if (path.equals("/queue")) {
                            retval = handleQueue(request, exchange);
                        } else if (path.equals("/process")) {
                            retval = handleProcess(request, exchange);
                        } else if (path.startsWith("/poll/")) {
                            retval = handlePoll(request, exchange, path.substring(6));
                        } else {
                            throw new HandlerException("not handled", 404);
                        }
                    } catch (HandlerException e) {
                        exc = e;
                    } catch (Exception e) {
                        exc = new HandlerException("internal server error", e, 500);
                    }
        
                    if (exc != null) {
                        log.log(Level.WARNING, "an error occurred", exc);
                        retval = new HashMap<String, Object>();
                        retval.put("status", "error");
                        retval.put("message", exc.getMessage());
                        if (exc.getCause() != null) {
                            retval.put("cause", exc.getCause().toString());
                        }
                    } else {
                        if (!retval.containsKey("status"))
                            retval.put("status", "success");
                    }
        
                    byte[] responseBody = null;
                    final MediaType type = MediaType.JSON_UTF_8.withCharset(jsonCharset);
                    final Charset responseCharset = setUpResponse(request, exchange, type);
                    responseBody = getGson().toJson(retval).getBytes(responseCharset);
                    OutputStream out = null;
                    try {
                        log.info("sending response to the client...");
                        exchange.sendResponseHeaders(exc != null ? exc.getStatus(): 200, responseBody.length);
                        out = exchange.getResponseBody();
                        out.write(responseBody);
                    } finally {
                        log.info("Closing...");
                        if (out != null) {
                            out.close();
                        }
                    }
                }
            } finally {
                exchange.close();
            }
        }
    }

    public Server(InetSocketAddress address, List<URI> originHosts, long gcInterval) {
        if (originHosts.size() == 0) {
            throw new IllegalArgumentException("no origin hosts given");
        }
        this.logWindow = new LogWindow();
        this.address = address;
        this.originHosts.addAll(originHosts);
        this.nextId = 0;
        this.gcInterval = gcInterval;
        this.queue = new LinkedBlockingQueue<Job>();
        this.printThread = createPrintThread();
        if (gcInterval > 0)
            this.gcThread = createGCThread();
    }

    private static InetSocketAddress parseAddress(final String listen) {
        final Matcher m = addrRegex.matcher(listen);
        if (!m.matches()) { 
            throw new ConfigurationException("could not parse addr-port specification: " + listen);
        }
        final String v6Address = m.group(1), v4Address = m.group(2);
        final String port = m.group(3);
        return new InetSocketAddress(
            InetAddresses.forString(v6Address == null ? v4Address: v6Address),
            Integer.parseInt(port)
        );
    }

    private static List<URI> parseOriginHosts(List<String> originHosts) {
        List<URI> _originHosts = new ArrayList<URI>();
        for (String originHost: originHosts) {
            try {
                _originHosts.add(new URI(originHost));
            } catch (URISyntaxException e) {
                throw new ConfigurationException("Malformed URI: " + originHost);
            }
        }
        return _originHosts;
    }

    public Server(String listen, List<String> originHosts, long gcInterval) {
        this(parseAddress(listen), parseOriginHosts(originHosts), gcInterval);
    }
 
    public Server(Configuration config) {
        this(config.getListen(), config.getOriginHosts(), config.getGCInterval());
    }

    public void setService(AppWindowService service) {
        this.service = service;
    }
 
    private void startPrintThread() {
        if (printThread != null)
            printThread.start();
        else
            disposed.countDown();
    }

    private void stopPrintThread() {
        printThreadIsRunning.set(false);
        printThread.interrupt();
        printThread = null;
    }

    private void startGCThread() {
        if (gcThread != null)
            gcThread.start();
        else
            disposed.countDown();
    }

    private void stopGCThread() {
        gcThreadIsRunning.set(false);
        gcThread.interrupt();
        gcThread = null;
    }

    private void startHttpServer() throws IOException {
        httpServer = HttpServer.create(address, 0);
        httpServer.createContext("/", new Handler());
        log.info("Starting HTTP server on " + address   );
        httpServer.start();
    }

    private void enableLogging() {
        final java.util.logging.Handler handler = new java.util.logging.Handler() {
            @Override
            public void close() throws SecurityException {
            }

            @Override
            public void flush() {
            }

            @Override
            public void publish(LogRecord record) {
                synchronized (Server.this) {
                    if (logWindow != null)
                        logWindow.appendLine(getFormatter().format(record));
                }
            }
        };
        handler.setFormatter(new SimpleFormatter());
        Logger.getLogger("").addHandler(handler);
    }

    public synchronized void start() {
        try {
            icon = makeSystemTray();
            SystemTray.getSystemTray().add(icon);
            enableLogging();

            printServices = new ArrayList<PrintService>();
            for (PrintService service: PrinterJob.lookupPrintServices()) {
                printServices.add(service);
            }
    
            log.info("Accept connection at " + address);
            icon.setToolTip("altair print server at " + address);
            statusLabel.setLabel("queue size is "+queue.size());
            for (URI h: originHosts) {
                log.info("Origin: " + h);
            }
            startHttpServer();
            startPrintThread();
            startGCThread();
        } catch (Exception e) {
            log.log(Level.SEVERE, "error occurred during starting server", e);
            throw new ServerRuntimeException("error occurred during starting server", e);
        }
    }

    public synchronized void stop() {
        SystemTray.getSystemTray().remove(icon);
        if (httpServer != null) {
            log.info("Stopping HTTP server");
            httpServer.stop(0);
            httpServer = null;
        }
        if (printThread != null) { 
            stopPrintThread();
        }
        if (gcThread != null) {
            stopGCThread();
        }
        if (logWindow != null) {
            logWindow.dispose();
            logWindow = null;
        }
        disposed.countDown();
    }

    public void run() {
        start();
        try {
            disposed.await();
        } catch (InterruptedException e) {
            log.log(Level.INFO, "interrupted", e);
        }
    }
    
    private TrayIcon makeSystemTray() throws IOException, AWTException {
        Image image = ImageIO.read(Server.class.getResourceAsStream("/trayicon.png"));
        
        PopupMenu menu = new PopupMenu();
        
        statusLabel = new MenuItem("hoge");
        statusLabel.setEnabled(false);
        menu.add(statusLabel);
        
        menu.addSeparator();
        MenuItem showLogWindowItem = new MenuItem("ログウィンドウ...");
        showLogWindowItem.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                logWindow.setVisible(true);
            }
        });
        menu.add(showLogWindowItem);
        MenuItem exitItem = new MenuItem("終了");
        exitItem.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                stop();
            }
        });
        menu.add(exitItem);
        return new TrayIcon(image, "altair print server", menu);
    }

    protected class LoaderListener<T extends ExtendedSVG12OMDocument> implements SVGDocumentLoaderListener, Future<T> {
        protected volatile boolean done = false;
        protected T result = null;
        protected Exception exception = null;
        
        @Override
        public boolean cancel(boolean mayInterruptIfRunning) {
            return false;
        }

        @Override
        public synchronized T get() throws InterruptedException, ExecutionException {
            if (!done) {
                log.info("waiting done...");
                wait();
                log.info("after wait()");
            }
            if (exception != null) {
                log.info("found exception");
                throw new ExecutionException(exception);
            }
            return result;
        }

        @Override
        public synchronized T get(long timeout, TimeUnit unit) throws InterruptedException, ExecutionException, TimeoutException {
            if (!done) {
                wait(unit.toMillis(timeout));
                if (!done) {
                    throw new TimeoutException();
                }
            }
            if (exception != null)
                throw new ExecutionException(exception);
            return result;
        }

        @Override
        public boolean isCancelled() {
            return false;
        }

        @Override
        public boolean isDone() {
            return done;
        }

        @Override
        public void documentLoadingStarted(SVGDocumentLoaderEvent e) {
            // do nothing
            log.info("dl started");
        }

        @SuppressWarnings("unchecked")
        @Override
        public void documentLoadingCompleted(SVGDocumentLoaderEvent e) {
            result = (T) e.getSVGDocument();
            done();
        }

        @Override
        public void documentLoadingCancelled(SVGDocumentLoaderEvent e) {
            exception = new Exception("cancelled");
            done();
            notifyAll();
        }

        @Override
        public void documentLoadingFailed(SVGDocumentLoaderEvent e) {
            log.info("dl failed");
            exception = ((SVGDocumentLoader)e.getSource()).getException();
            done();
        }
        
        private void done() {
            done = true;
            synchronized (this) {
                notifyAll();
            }
        }
    }
    
    private int getNextId() {
        synchronized (this) {
            return nextId++;
        }
    }

    private void processRequest(final Job job) throws IOException {
        job.id = getNextId();
        synchronized (jobsBeingProcessed) {
            jobsBeingProcessed.put(job.id, job);
        }
        try {
            if (!queue.offer(job, 1, TimeUnit.SECONDS)) {
                log.severe("queue timeout");
            } else {
                log.info(String.format("Job(id=%d) added to queue", job.id));
                statusLabel.setLabel("Queue size is " + queue.size());
            }
        } catch (InterruptedException e) {
            log.log(Level.SEVERE, "interrupted", e);
        }
    }

    private Thread createPrintThread() {
        return threadFactory.newThread(
            new Runnable() {
                @Override
                public void run() {
                    log.info("Starting printing thread");
                    printThreadIsRunning.set(true);
                    AccessController.doPrivileged(new PrivilegedAction<Object>() {
                        public Object run() {
                            while (printThreadIsRunning.get()) {
                                try {
                                    final Job job = queue.take();
                                    log.info("Take " + job);
                                    final OurDocumentLoader loader = new OurDocumentLoader(service);
                                    final ExtendedSVG12BridgeContext bridgeContext = new ExtendedSVG12BridgeContext(service);
                                    bridgeContext.setInteractive(false);
                                    bridgeContext.setDynamic(false);
                                    try {
                                        if (job.svg != null) {
                                            // SVGをオブジェクトにする
                                            log.info("Creating page set model");
                                            InputStream is = new ByteArrayInputStream(UTF_8_CHARSET.encode(job.svg).array());
                                            ExtendedSVG12OMDocument doc = (ExtendedSVG12OMDocument) loader.loadDocument("http://", is);
                                            job.pageSet = new PageSetModel(bridgeContext, doc);
                                        } else {
                                            // altairに要求してSVGを取得する
                                            URLConnection conn = (new URL(job.peekUrl)).openConnection();
                                            conn.setRequestProperty("Cookie", job.cookie);
                                            conn.setUseCaches(false);
                                            URLConnectionSVGDocumentLoader documentLoader = new URLConnectionSVGDocumentLoader(conn, new RequestBodySender() {
                                                public String getRequestMethod() {
                                                    return "POST";
                                                }
        
                                                public void send(OutputStream out) throws IOException {
                                                    log.info("Sending " + job);
                                                    final JsonWriter writer = new JsonWriter(new OutputStreamWriter(out, "utf-8"));
                                                    writer.beginObject();
                                                    writer.name("ticket_format_id").value(job.ticketFormatId);
                                                    writer.name("page_format_id").value(job.pageFormatId);
                                                    if (job.orderId != null) {
                                                        writer.name("order_id").value(job.orderId);
                                                    } else if (job.queueIds != null && !job.queueIds.isEmpty()) {
                                                        writer.name("queue_ids");
                                                        writer.beginArray();
                                                        for (Integer queueId: job.queueIds) {
                                                            writer.value(queueId);
                                                        }
                                                        writer.endArray();
                                                    }
                                                    writer.endObject();
                                                    writer.flush();
                                                    writer.close();
                                                }
                                            }, loader);
                                            LoaderListener<ExtendedSVG12OMDocument> listener = new LoaderListener<ExtendedSVG12OMDocument>();
                                            documentLoader.addSVGDocumentLoaderListener(listener);
                                            log.info("Starting documentLoader");
                                            documentLoader.start();
                                 
                                            log.info("Awaiting response");
                                            ExtendedSVG12OMDocument doc = listener.get();        // ここで取得完了を待つ
                                            if (listener.exception != null) {
                                                throw listener.exception;
                                            }
                                            final PageSetModel pageSet = new PageSetModel(bridgeContext, doc);
                                            log.info("Number of pages: " + pageSet.getPages().size());
                                            // dequeueする際に必要になるのでページからqueueIdを抽出する
                                            final List<Integer> actualQueueIds = new ArrayList<Integer>();
                                            for (Page page: pageSet.getPages()) {
                                                log.info(String.format("Queue IDs for page %s: %s", page.getName(), Joiner.on(",").join(page.getQueueIds())));
                                                for (String queueId: page.getQueueIds()) {
                                                    actualQueueIds.add(Integer.parseInt(queueId));
                                                }
                                            }
                                            job.pageSet = pageSet;
                                            job.queueIds = actualQueueIds;
                                        }
                                        PrinterJob printerJob = makePrinterJob(job);
                                        log.info("Start printing...");
                                        printerJob.print();
                                        log.info("Printing completed");                                        
                                        log.info(job + " completed");
                                        try {
                                            notifyCompletion(job);
                                        } finally {
                                            job.disposeAndSet(null);
                                        }
                                    } catch (Exception e) {
                                        log.log(Level.SEVERE, "Failed to print out.", e);
                                        job.disposeAndSet(e);
                                    }
                                } catch (InterruptedException e) {
                                    log.info("Printing thread was interrupted");
                                    continue;
                                }
                            }
                            return null;
                        }
                    });
                    log.info("Printing thread terminated");
                    disposed.countDown();
                }
            }
        );
    }

    private Thread createGCThread() {
        return threadFactory.newThread(new Runnable() {
            @Override
            public void run() {
                gcThreadIsRunning.set(true);
                                            log.info(String.format("GC Thread started (interval=%d)", gcInterval));
                while (gcThreadIsRunning.get()) {
                    try {
                        Thread.sleep(gcInterval);
                    } catch (InterruptedException e) {
                        gcThreadIsRunning.set(false);
                        continue;
                    }
                    log.info("GC thread is picking jobs being processed");
                    List<Job> jobs = null;
                    synchronized (jobsBeingProcessed) {
                        jobs = new ArrayList<Job>(jobsBeingProcessed.values());
                    }
                    final Date now = new Date();
                    for (final Job job: jobs) {
                        if (job.isDone()) {
                            final long elapsed = now.getTime() - job.createdAt.getTime();
                            if (elapsed > gcInterval) {
                                log.info(job + " is stale");
                                synchronized (jobsBeingProcessed) {
                                    jobsBeingProcessed.remove(job.id);
                                }
                            }
                        }
                    }
                }
                log.info("GC Thread terminated");
                disposed.countDown();
            }
        });
    }
    
    private List<PrintService> printServices;
    
    public List<PrintService> getPrintServices() {
        return printServices;
    }
    
    private void notifyCompletion(Job job) {
        if (job.queueIds != null && !job.queueIds.isEmpty()) {
            log.info("Sending completion notification for " + job);
            try {
                final HttpURLConnection conn = (HttpURLConnection) (new URL(job.dequeueUrl)).openConnection();
                conn.setRequestProperty("Cookie", job.cookie);
                conn.setUseCaches(false);
                conn.setRequestMethod("POST");
                conn.setDoOutput(true);
                OutputStream out = conn.getOutputStream();
                JsonWriter writer = new JsonWriter(new OutputStreamWriter(out, "utf-8"));
                writer.beginObject();
                writer.name("queue_ids");
                writer.beginArray();
                for (int queueId: job.queueIds) {
                    writer.value(queueId);
                }
                writer.endArray();
                writer.endObject();
                writer.flush();
                writer.close();
                
                int code = conn.getResponseCode();
                if (code != 200)
                    throw new CommunicationException("Server returned error status: " + code);
                final JsonObject obj = new JsonParser().parse(new InputStreamReader(conn.getInputStream())).getAsJsonObject();
                if (obj.has("status")) {
                    if (obj.get("status").getAsString().equals("success")) {
                        log.info("Dequeued " + job);
                    } else {
                        log.severe(String.format("Failed to dequeue %s (reason: %s)", job, obj.get("message")));
                        // dequeueに失敗
                        // TODO: 常駐している限りは、リトライしたい。。。原因によるが。
                    }
                } else {
                    throw new CommunicationException("server returned unexpected response");
                }
            } catch(Exception e) {
                log.log(Level.SEVERE, "oops", e);
            }
        }
        statusLabel.setLabel("Queue size is " + queue.size());
    }
    
    private PrinterJob makePrinterJob(Job job) throws PrinterException {
        PrinterJob printerJob = PrinterJob.getPrinterJob();
        TicketPrintable content = new TicketPrintable(
            new ArrayList<Page>(job.pageSet.getPages()),
            printerJob,
            new AffineTransform(72. / 90, 0, 0, 72. / 90, 0, 0)
        );
        printerJob.setPrintService(getPrintServiceByName(job.printer));
        printerJob.setPrintable(content, job.pageFormat);
        
        return printerJob;
    }

    public static List<String> findPageTitles(PageSetModel pageSetModel, ExtendedSVG12OMDocument doc) {
        final List<String> titles = new ArrayList<String>();
        final Iterator<SVGOMPageElement> i = new PageElementIterator(pageSetModel.findPageSetElement(doc));
        while (i.hasNext()) {
            final SVGOMPageElement page = i.next();
            titles.add(findTitle(page));
        }
        return titles;
    }
    
    // copied from PageSetModel
    private static String findTitle(SVGOMElement elem) {
        for (Node n = elem.getFirstChild(); n != null; n = n.getNextSibling()) {
            if (n instanceof SVGOMTitleElement) {
                return n.getTextContent();
            }
        }
        return null;
    }
    
    private PrintService getPrintServiceByName(String name) {
        for(PrintService ps: getPrintServices()) {
            if(ps.getName().equals(name)) {
                return ps;
            }
        }
        return null;
    }
}
