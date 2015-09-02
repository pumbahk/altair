package jp.ticketstar.ticketing.printing;

import java.awt.AWTException;
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
import java.io.PrintStream;
import java.net.HttpURLConnection;
import java.net.InetSocketAddress;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLConnection;
import java.nio.charset.Charset;
import java.security.AccessController;
import java.security.PrivilegedAction;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Queue;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

import javax.imageio.ImageIO;
import javax.print.PrintService;

import jp.ticketstar.ticketing.RequestBodySender;
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
import org.kohsuke.args4j.Option;
import org.w3c.dom.Node;

import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.google.gson.stream.JsonWriter;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;


@SuppressWarnings("restriction")
public class Server implements HttpHandler {
    private AppWindowService service;
    
    @Option(name="--server")
    private boolean acceptConnection;
    
    @Option(name="--port")
    private int port;
    
    @Option(name="--origin")
    private List<String> originHosts;
    
    @Option(name="--queue")
    private boolean useQueue;
    
    private PrintStream console;
    
    private int nextId;
    private Queue<Job> queue;
    
    private Object printThreadLock;
    private Thread printThread;
    
    private TrayIcon icon;
    private MenuItem statusLabel;
    
    class Job {
        Integer id;
        
        String printer;
        OurPageFormat pageFormat;
        String svg;
        
        String uri;
        String cookie;
        int page_format_id;
        int ticket_format_id;
        int[] queueIds;
        
        PageSetModel pageSet;
    }
    
    public Server() {
        acceptConnection = false;
        port = 8081;
        originHosts = new ArrayList<String>();
        useQueue = false;
        
        console = System.out;
        
        nextId = 0;
        queue = new LinkedList<Job>();
        
        printThreadLock = new Object();
        printThread = null;
    }
    
    public boolean acceptConnection() {
        return acceptConnection;
    }
    
    public int getPort() {
        return port;
    }
    
    public void setService(AppWindowService service) {
        this.service = service;
    }
    
    public void start() {
        try {
            icon = makeSystemTray();
            SystemTray.getSystemTray().add(icon);
        } catch(IOException e) {
            e.printStackTrace(console);
        } catch(AWTException e) {
            e.printStackTrace(console);
        }
        
        printServices = new ArrayList<PrintService>();
        for (PrintService service: PrinterJob.lookupPrintServices()) {
            printServices.add(service);
        }
        
        console.println("Accept connection at port "+port);
        icon.setToolTip("altair print server at port "+port);
        statusLabel.setLabel("queue size is "+queue.size());
        for(String h: originHosts) {
            console.println("Origin: "+h);
        }
        
        try {
            HttpServer httpServer = HttpServer.create(new InetSocketAddress(getPort()), 0);
            httpServer.createContext("/", this);
            httpServer.start();
        } catch(IOException e) {
            e.printStackTrace(console);
            System.exit(0);
        }
    }
    
    private TrayIcon makeSystemTray() throws IOException, AWTException {
        Image image = ImageIO.read(Server.class.getResourceAsStream("/trayicon.png"));
        
        PopupMenu menu = new PopupMenu();
        
        statusLabel = new MenuItem("hoge");
        statusLabel.setEnabled(false);
        menu.add(statusLabel);
        
        menu.addSeparator();
        
        MenuItem exitItem = new MenuItem("終了");
        exitItem.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                System.exit(0);
            }
        });
        menu.add(exitItem);
        return new TrayIcon(image, "altair print server", menu);
    }


    @Override
    public void handle(HttpExchange exchange) throws IOException {
        // クライアントとリクエストを表示する
        console.println("new connection from "+exchange.getRemoteAddress().toString()+" with request "+exchange.getRequestMethod()+" "+exchange.getRequestURI());
        
        StringBuffer sb = new StringBuffer();
        
        String path = exchange.getRequestURI().getPath();

        boolean preferJson = getJsonAcception(exchange);
        
        List<String> origins = exchange.getRequestHeaders().get("Origin");
        if(origins != null && origins.size() == 1) {
            String origin = origins.get(0);
            if(originHosts.contains(origin)) {
                exchange.getResponseHeaders().add("Access-Control-Allow-Origin", origin);
            }
        }
        exchange.getResponseHeaders().add("Access-Control-Allow-Headers", "Accept,Content-Type");
        
        String type = "text/plain; charset=UTF-8";
        OutputStream out = exchange.getResponseBody();
        Gson gson = new Gson();
        try {
            if(path.equals("/printers")) {
                if(preferJson) {
                    type = "text/json; charset=UTF-8";
                    Map<String,Object> data = new HashMap<String,Object>();
                    List<String> list = new ArrayList<String>();
                    for(PrintService ps: getPrintServices()) {
                        list.add(ps.getName());
                    }
                    data.put("printers", list);
                    sb.append(gson.toJson(data));
                } else {
                    for(PrintService ps: getPrintServices()) {
                        sb.append(ps.getName()+"\n");
                    }
                }
            } else if(path.equals("/queue")) {
                Map<String,Object> data = new HashMap<String,Object>();
                List<String> list = new ArrayList<String>();
                synchronized (queue) {
                    for(Job job: queue.toArray(new Job[0])) {
                        if(preferJson) {
                            list.add("job-"+job.id);
                        } else {
                            sb.append("job "+job.id+"\n");
                        }
                    }
                }
                if(preferJson) {
                    type = "text/json; charset=UTF-8";
                    data.put("jobs", list);
                    sb.append(gson.toJson(data));
                }
            } else if(path.equals("/process") && exchange.getRequestMethod().equals("POST")) {
                type = "text/json; charset=UTF-8";
                
                // リクエストをオブジェクトとして読み込む
                console.println("Building request");
                Job job = new Job();
                JsonObject obj = new JsonParser().parse(new InputStreamReader(exchange.getRequestBody(), "UTF-8")).getAsJsonObject();
                /*
                char[] buf = new char[1024];
                new BufferedReader(new InputStreamReader(exchange.getRequestBody(), "UTF-8")).read(buf);
                JsonObject obj = new JsonParser().parse(new String(buf)).getAsJsonObject();
                */
                job.printer = obj.get("printer").getAsString();
                job.pageFormat = FormatLoader.buildPageFormat(obj.get("page").getAsJsonObject());
                
                try {
                    job.uri = obj.get("uri").getAsString();
                    job.cookie = obj.get("cookie").getAsString();
                    job.page_format_id = obj.get("page_format_id").getAsInt();
                    job.ticket_format_id = obj.get("ticket_format_id").getAsInt();
                    JsonArray queueIds = obj.get("queue_ids").getAsJsonArray();
                    job.queueIds = new int[queueIds.size()];
                    for(int i=0 ; i<queueIds.size(); i++) {
                        job.queueIds[i] = queueIds.get(i).getAsInt();
                    }
                } catch(NullPointerException e) {
                    // ignore
                }
                
                console.println("Processing...");
                if(obj.has("svg")) {
                    processRequest(job, obj.get("svg").getAsString());
                } else {
                    processRequest(job, null);
                }
                
                Map<String,Object> data = new HashMap<String,Object>();
                data.put("status", "OK");
                sb.append(gson.toJson(data));
                
                console.println("finish output.");
            } else if(path.equals("/test")) {
                /*
                String str = "{}";
                JsonObject result = new JsonParser().parse(str).getAsJsonObject();
                FormatPair fp = FormatLoader.buildFormatsFromJsonObject(result.get("data").getAsJsonObject());
                fp.pageFormats
                URI uri = null;
                try {
                    uri = new URI("file:///tmp/sample1.svg");
                } catch(URISyntaxException e) {
                    e.printStackTrace();
                }
                if(uri != null) {
                    service.loadDocument(uri);
                    service.printAll();
                }
                */
            } else {
                console.println("not handled.");
            }
            
            byte[] bytes = sb.toString().getBytes(Charset.forName("UTF-8"));
            exchange.getResponseHeaders().add("Content-Type", type);
            exchange.sendResponseHeaders(200, bytes.length);
            out.write(bytes);
        } catch(Exception e) {
            console.println("Catch exception");
            e.printStackTrace(console);
            
            sb.append("\n");
            sb.append(e.getMessage());
            
            byte[] bytes = sb.toString().getBytes(Charset.forName("UTF-8"));
            exchange.getResponseHeaders().add("Content-Type", type);
            exchange.sendResponseHeaders(200, bytes.length);
            out.write(bytes);
        } finally {
            console.println("Closing...");
            out.close();
            exchange.close();
        }
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
                console.println("waiting done...");
                wait();
                console.println("after wait()");
            }
            if (exception != null) {
                console.println("found exception");
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
            console.println("dl started");
        }

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
            console.println("dl failed");
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
    
    private void processRequest(final Job job, String svg) throws IOException {
        OurDocumentLoader loader = new OurDocumentLoader(service);
        ExtendedSVG12BridgeContext bridgeContext = new ExtendedSVG12BridgeContext(service);
        bridgeContext.setInteractive(false);
        bridgeContext.setDynamic(false);
        
        if(svg != null) {
            // SVGをオブジェクトにする
            console.println("creating page set model");
            InputStream is = new ByteArrayInputStream(svg.getBytes("utf-8"));
            ExtendedSVG12OMDocument doc = (ExtendedSVG12OMDocument) loader.loadDocument("http://", is);
            job.pageSet = new PageSetModel(bridgeContext, doc);
        } else {
            // altairに要求してSVGを取得する
            URLConnection conn = (new URL(job.uri+"/tickets/print/peek")).openConnection();
            conn.setRequestProperty("Cookie", job.cookie);
            conn.setUseCaches(false);
            console.println("using "+job.uri+"/tickets/print/peek");
            
            URLConnectionSVGDocumentLoader documentLoader = new URLConnectionSVGDocumentLoader(conn, new RequestBodySender() {
                public String getRequestMethod() {
                    return "POST";
                }

                public void send(OutputStream out) throws IOException {
                    /*
                    OutputStream original = out;
                    ByteArrayOutputStream bOut = new ByteArrayOutputStream();
                    out = bOut;
                    */
                    final JsonWriter writer = new JsonWriter(new OutputStreamWriter(out, "utf-8"));
                    writer.beginObject();
                    writer.name("ticket_format_id").value(job.ticket_format_id);
                    writer.name("page_format_id").value(job.page_format_id);
                    /*
                    if (0 < job.order_id) {
                        writer.name("order_id");
                        writer.value(orderId);
                    }
                    */
                    if(job.queueIds != null && 0 < job.queueIds.length) {
                        writer.name("queue_ids");
                        writer.beginArray();
                        for (int queueId: job.queueIds) {
                            writer.value(queueId);
                        }
                        writer.endArray();
                    }
                    writer.endObject();
                    writer.flush();
                    writer.close();
                    /*
                    console.println(bOut.toString("utf-8"));
                    original.write(bOut.toByteArray());
                    */
                }
            }, loader);
            LoaderListener<ExtendedSVG12OMDocument> listener = new LoaderListener<ExtendedSVG12OMDocument>();
            documentLoader.addSVGDocumentLoaderListener(listener);
            console.println("start documentLoader");
            documentLoader.start();
            
            try {
                console.println("wait response");
                ExtendedSVG12OMDocument doc = listener.get();        // ここで取得完了を待つ
                job.pageSet = new PageSetModel(bridgeContext, doc);
                console.println("done");
            } catch(InterruptedException e) {
                e.printStackTrace(console);
            } catch(ExecutionException e) {
                e.printStackTrace(console);
            }
        }
        
        if(useQueue) {
            console.println("Add to queue");
            synchronized (queue) {
                job.id = nextId++;
                queue.add(job);
            }
            console.println("ok");
            statusLabel.setLabel("queue size is "+queue.size());
            
            synchronized (printThreadLock) {
                if(printThread == null) {
                    console.println("Starting print thread...");
                    printThread = createPrintThread();
                    printThread.start();
                } else {
                    console.println("already running: "+printThread.hashCode());
                }
            }
        } else {
            // キューなんて使わずに直接スレッドで
            console.println("Creating thread...");
            final Job _job = job;
            Thread thread = new Thread(new Runnable() {
                public void run() {
                    AccessController.doPrivileged(new PrivilegedAction<Object>() {
                        public Object run() {
                            try {
                                PrinterJob printerJob = makePrinterJob(_job);
                                if(printerJob != null) {
                                    printerJob.print();
                                    notifyCompletion(_job);
                                    console.println("child completed.");
                                } else {
                                    console.println("no such printer");
                                }
                            } catch(PrinterException e) {
                                e.printStackTrace(console);
                            }
                            return null;
                        }
                    });
                }
            });
            thread.start();
        }
    }

    private boolean getJsonAcception(HttpExchange exchange) {
        // FIXME: もうちょっと真面目にパースしよう
        String query = exchange.getRequestURI().getQuery();
        if(query != null && query.contains("as=json")) {
            return true;
        }
        
        List<String> accepts = exchange.getRequestHeaders().get("Accept");
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
    
    private Thread createPrintThread() {
        class Box {
            int identity;
        }
        final Box box = new Box();
        Thread thread = new Thread(new Runnable() {
            public void run() {
                AccessController.doPrivileged(new PrivilegedAction<Object>() {
                    public Object run() {
                        String prefix = "["+box.identity+"] ";
                        console.println(prefix+"starting printing thread");
                        while(true) {
                            Job job = null;
                            synchronized (queue) {
                                job = queue.peek();
                            }
                            if(job == null) {
                                synchronized (printThreadLock) {
                                    console.println(prefix+"No more job, terminate thread.");
                                    printThread = null;
                                }
                                return null;
                            }
                            console.println(prefix+"Found job "+job.id);
                            try {
                                PrinterJob printerJob = makePrinterJob(job);
                                console.println(prefix+"Start printing...");
                                printerJob.print();
                                console.println(prefix+"Printing completed.");
                                notifyCompletion(job);
                                synchronized (queue) {
                                    queue.poll();
                                }
                                statusLabel.setLabel("queue size is "+queue.size());
                                Thread.sleep(1000);
                            } catch(PrinterException e) {
                                // プリンタの問題が起きた場合は...
                                e.printStackTrace(console);
                                System.exit(0);
                            } catch(InterruptedException e) {
                                e.printStackTrace(console);
                            }
                        }
                    }
                });
            }
        });
        box.identity = thread.hashCode();
        return thread;
    }
    
    private List<PrintService> printServices;
    
    public List<PrintService> getPrintServices() {
        return printServices;
    }
    
    private void notifyCompletion(Job job) {
        if(job.queueIds != null && 0 < job.queueIds.length) {
            try {
                HttpURLConnection conn = (HttpURLConnection) (new URL(job.uri+"/tickets/print/dequeue")).openConnection();
                conn.setRequestProperty("Cookie", job.cookie);
                conn.setUseCaches(false);
                conn.setRequestMethod("POST");
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
                
                JsonObject obj = new JsonParser().parse(new InputStreamReader(conn.getInputStream())).getAsJsonObject();
                if(obj.has("status")) {
                    if(obj.get("status").getAsString().equals("success")) {
                        // OK
                    } else {
                        // dequeueに失敗
                        // TODO: 常駐している限りは、リトライしたい。。。原因によるが。
                    }
                }
            } catch(MalformedURLException e) {
                e.printStackTrace(console);
            } catch(IOException e) {
                e.printStackTrace(console);
            }
        }
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
        List<String> titles = new ArrayList<String>();
        Iterator<SVGOMPageElement> i = new PageElementIterator(pageSetModel.findPageSetElement(doc));
        while(i.hasNext()) {
            SVGOMPageElement page = i.next();
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
