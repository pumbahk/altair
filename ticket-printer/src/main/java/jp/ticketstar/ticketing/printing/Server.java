package jp.ticketstar.ticketing.printing;

import java.awt.geom.AffineTransform;
import java.awt.print.PrinterJob;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.net.URI;
import java.net.URISyntaxException;
import java.nio.charset.Charset;
import java.security.AccessController;
import java.security.PrivilegedAction;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

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
	
	@Option(name="--server")
    private boolean acceptConnection;
	
	@Option(name="--port")
    private int port;
	
	@Option(name="--origin")
	private List<String> originHosts;
	
	public Server() {
		acceptConnection = false;
		port = 8081;
		originHosts = new ArrayList<String>();
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
		for(String h: originHosts) {
			System.out.println("Origin: "+h);
		}
		
		HttpServer httpServer = HttpServer.create(new InetSocketAddress(getPort()), 0);
		httpServer.createContext("/", this);
		httpServer.start();
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
		System.out.println("new connection from "+exchange.getRemoteAddress().toString()+" with request "+exchange.getRequestMethod()+" "+exchange.getRequestURI());
		
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
			} else if(path.equals("/process") && exchange.getRequestMethod().equals("POST")) {
				type = "text/json; charset=UTF-8";
				
				InputStreamReader isr = new InputStreamReader(exchange.getRequestBody(), "UTF-8");
				Request req = gson.fromJson(isr, Request.class);
				
				ExtendedSVG12BridgeContext bridgeContext = new ExtendedSVG12BridgeContext(service);
				bridgeContext.setInteractive(false);
				bridgeContext.setDynamic(false);
				
				InputStream is = new ByteArrayInputStream(req.svg.getBytes("utf-8"));
				OurDocumentLoader loader = new OurDocumentLoader(service);
				ExtendedSVG12OMDocument doc = (ExtendedSVG12OMDocument) loader.loadDocument("http://", is);
				
				model.setPageSetModel(new PageSetModel(bridgeContext, doc));
				
				// ページ一覧を出してみる
				Iterator<SVGOMPageElement> i = new PageElementIterator(model.getPageSetModel().findPageSetElement(doc));
				while(i.hasNext()) {
					SVGOMPageElement page = i.next();
					final String title = findTitle(page);
					System.out.println("[page] "+title);
				}
				
				System.out.println("Creating thread...");
				Thread thread = new Thread(new Runnable() {
					public void run() {
						AccessController.doPrivileged(new PrivilegedAction<Object>() {
							public Object run() {
								try {
									final PrinterJob job = PrinterJob.getPrinterJob();
									job.setPrintService(model.getPrintService());
									job.setPrintable(createTicketPrintable(job), model.getPageFormat());
									job.print();
								} catch (Exception e) {
									e.printStackTrace();
								}
								// 完了!
								System.out.println("child completed.");
								return null;
							}
						});
					}
				});
				thread.start();
				
				Map<String,Object> data = new HashMap<String,Object>();
				data.put("status", "OK");
				sb.append(gson.toJson(data));
				
				System.out.println("finish output.");
			} else if(path.equals("/test")) {
				try {
					URI uri = new URI("file:///tmp/sample1.svg");
					service.loadDocument(uri);
					System.out.println("Printing...");
					service.printAll();
					System.out.println("done.");
				} catch(URISyntaxException e) {
					e.printStackTrace();
				}
			} else {
				System.out.println("not handled.");
			}
			
			byte[] bytes = sb.toString().getBytes(Charset.forName("UTF-8"));
			exchange.getResponseHeaders().add("Content-Type", type);
			exchange.sendResponseHeaders(200, bytes.length);
			out.write(bytes);
		} catch(Exception e) {
			System.out.println("Catch exception");
			e.printStackTrace(System.out);
			
			sb.append("\n");
			sb.append(e.getMessage());
			
			byte[] bytes = sb.toString().getBytes(Charset.forName("UTF-8"));
			exchange.getResponseHeaders().add("Content-Type", type);
			exchange.sendResponseHeaders(200, bytes.length);
			out.write(bytes);
		} finally {
			System.out.println("Closing...");
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
	
	// copied from BasicAppService
	protected TicketPrintable createTicketPrintable(PrinterJob job) {
		if (model.getPageSetModel() == null) {
			throw new IllegalStateException("pageSetModel is not loaded");
		}
		return new TicketPrintable(
			new ArrayList<Page>(model.getPageSetModel().getPages()),
			job,
			new AffineTransform(72. / 90, 0, 0, 72. / 90, 0, 0)
		);
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

}
