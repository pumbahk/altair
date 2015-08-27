package jp.ticketstar.ticketing.printing;

import java.awt.geom.AffineTransform;
import java.awt.print.PrinterException;
import java.awt.print.PrinterJob;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.PrintStream;
import java.net.InetSocketAddress;
import java.net.URI;
import java.net.URISyntaxException;
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

import javax.print.PrintService;

import jp.ticketstar.ticketing.printing.gui.AppWindowModel;
import jp.ticketstar.ticketing.printing.gui.AppWindowService;
import jp.ticketstar.ticketing.svg.ExtendedSVG12BridgeContext;
import jp.ticketstar.ticketing.svg.ExtendedSVG12OMDocument;
import jp.ticketstar.ticketing.svg.OurDocumentLoader;
import jp.ticketstar.ticketing.svg.SVGOMPageElement;

import org.apache.batik.dom.svg.SVGOMElement;
import org.apache.batik.dom.svg.SVGOMTitleElement;
import org.kohsuke.args4j.Option;
import org.w3c.dom.Node;

import com.google.gson.Gson;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;


@SuppressWarnings("restriction")
public class Server implements HttpHandler {
	private AppWindowModel model;
	private AppWindowService service;
	private ExtendedSVG12BridgeContext bridgeContext;
	
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
	
	public void setModel(AppWindowModel model) {
		this.model = model;
	}

	public void setService(AppWindowService service) {
		this.service = service;
	}
	
	public void start() throws IOException {
		console.println("Accept connection at port "+port);
		for(String h: originHosts) {
			console.println("Origin: "+h);
		}
		
		bridgeContext = new ExtendedSVG12BridgeContext(service);
		bridgeContext.setInteractive(false);
		bridgeContext.setDynamic(false);
		
		HttpServer httpServer = HttpServer.create(new InetSocketAddress(getPort()), 0);
		httpServer.createContext("/", this);
		httpServer.start();
	}
	
	class Job {
		Integer id;
		Request request;
		PageSetModel pageSet;
	}
	
	class Request {
		String printer;
		String page;
		String svg;
		String uri;
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
					for(PrintService ps: model.getPrintServices()) {
						list.add(ps.getName());
					}
					data.put("printers", list);
					sb.append(gson.toJson(data));
				} else {
					PrintService selected = service.getPrintService();
					for(PrintService ps: model.getPrintServices()) {
						sb.append(selected.equals(ps) ? "* " : "  ");
						sb.append(ps.getName()+"\n");
					}
				}
			} else if(path.equals("/pages")) {
				if(preferJson) {
					type = "text/json; charset=UTF-8";
					Map<String,Object> data = new HashMap<String,Object>();
					List<String> list = new ArrayList<String>();
					for(OurPageFormat pf: model.getPageFormats()) {
						list.add(pf.getName());
					}
					data.put("pages", list);
					sb.append(gson.toJson(data));
				} else {
					OurPageFormat selected = service.getPageFormat();
					for(OurPageFormat pf: model.getPageFormats()) {
						sb.append(selected.equals(pf) ? "* " : "  ");
						sb.append(pf.getName()+"\n");
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
				Request req = gson.fromJson(new InputStreamReader(exchange.getRequestBody(), "UTF-8"), Request.class);
				
				// SVGをオブジェクトにする
				console.println("creating page set model");
				InputStream is = new ByteArrayInputStream(req.svg.getBytes("utf-8"));
				OurDocumentLoader loader = new OurDocumentLoader(service);
				ExtendedSVG12OMDocument doc = (ExtendedSVG12OMDocument) loader.loadDocument("http://", is);
				PageSetModel pageSetModel = new PageSetModel(bridgeContext, doc);
				
				Job job = new Job();
				job.request = req;
				job.pageSet = pageSetModel;
				
				if(useQueue) {
					console.println("Add to queue");
					synchronized (queue) {
						job.id = nextId++;
						queue.add(job);
					}
					console.println("ok");
					
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
				
				Map<String,Object> data = new HashMap<String,Object>();
				data.put("status", "OK");
				sb.append(gson.toJson(data));
				
				console.println("finish output.");
			} else if(path.equals("/test")) {
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
								synchronized (queue) {
									queue.poll();
								}
								Thread.sleep(1000);
							} catch (Exception e) {
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
	
	private PrinterJob makePrinterJob(Job job) throws PrinterException {
		PrinterJob printerJob = PrinterJob.getPrinterJob();
		TicketPrintable content = new TicketPrintable(
			new ArrayList<Page>(job.pageSet.getPages()),
			printerJob,
			new AffineTransform(72. / 90, 0, 0, 72. / 90, 0, 0)
		);
		printerJob.setPrintService(getPrintServiceByName(job.request.printer));
		printerJob.setPrintable(content, getPageFormatByName(job.request.page));
		
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
		for(PrintService ps: model.getPrintServices()) {
			if(ps.getName().equals(name)) {
				return ps;
			}
		}
		return null;
	}
	
	private OurPageFormat getPageFormatByName(String name) {
		for(OurPageFormat pf: model.getPageFormats()) {
			if(pf.getName().equals(name)) {
				return pf;
			}
		}
		return null;
	}

}
