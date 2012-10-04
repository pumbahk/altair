package jp.ticketstar.ticketing.printing.gui;

import java.net.URI;
import java.net.URLConnection;
import java.awt.Point;
import java.awt.geom.AffineTransform;
import java.awt.geom.Dimension2D;
import java.beans.PropertyChangeListener;
import java.util.List;

import javax.print.PrintService;

import org.apache.batik.bridge.BridgeExtension;
import org.apache.batik.bridge.ExternalResourceSecurity;
import org.apache.batik.bridge.ScriptSecurity;
import org.apache.batik.gvt.event.EventDispatcher;
import org.apache.batik.util.ParsedURL;
import org.w3c.dom.Element;
import org.w3c.dom.svg.SVGAElement;
import org.w3c.dom.svg.SVGDocument;

import jp.ticketstar.ticketing.printing.Page;
import jp.ticketstar.ticketing.ApplicationException;
import jp.ticketstar.ticketing.RequestBodySender;
import jp.ticketstar.ticketing.SerializingExecutor;
import jp.ticketstar.ticketing.printing.OurPageFormat;
import jp.ticketstar.ticketing.printing.StandardAppService;
import jp.ticketstar.ticketing.printing.TicketFormat;

public class AppAppletService implements StandardAppService {
	private AppAppletServiceImpl impl;
	private final SerializingExecutor executor;

	public void printAll() {
		executeSynchronously(new Runnable() {
			public void run() {
				impl.printAll();
			}
		});
	}

	public void displayError(String message) {
		impl.displayError(message);
	}

	public void displayError(Exception ex) {
		impl.displayError(ex);
	}

	public void displayMessage(String message) {
		impl.displayMessage(message);
	}

	public void showAlert(String message) {
		impl.showAlert(message);
	}

	public String showPrompt(String message) {
		return impl.showPrompt(message);
	}

	public String showPrompt(String message, String defaultValue) {
		return impl.showPrompt(message, defaultValue);
	}

	public boolean showConfirm(String message) {
		return impl.showConfirm(message);
	}

	public void deselectAll() {
		impl.deselectAll();
	}

	public float getPixelUnitToMillimeter() {
		return impl.getPixelUnitToMillimeter();
	}

	public Point getClientAreaLocationOnScreen() {
		return impl.getClientAreaLocationOnScreen();
	}

	public float getPixelToMM() {
		return impl.getPixelToMM();
	}

	public EventDispatcher getEventDispatcher() {
		return impl.getEventDispatcher();
	}

	public AffineTransform getTransform() {
		return impl.getTransform();
	}

	public Dimension2D getViewportSize() {
		return impl.getViewportSize();
	}

	public String getDefaultFontFamily() {
		return impl.getDefaultFontFamily();
	}

	public boolean hasFeature(String arg0) {
		return impl.hasFeature(arg0);
	}

	public float getMediumFontSize() {
		return impl.getMediumFontSize();
	}

	public void registerExtension(BridgeExtension arg0) {
		impl.registerExtension(arg0);
	}

	public float getLighterFontWeight(float f) {
		return impl.getLighterFontWeight(f);
	}

	public List<OurPageFormat> getPageFormats() {
		return impl.getPageFormats();
	}

	public String getLanguages() {
		return impl.getLanguages();
	}

	public OurPageFormat getPageFormat() {
		return impl.getPageFormat();
	}

	public void setPageFormat(final OurPageFormat pageFormat) {
		executeSynchronously(new Runnable() {
			public void run() {
				impl.setPageFormat(pageFormat);
			}
		});
	}

	public String getUserStyleSheetURI() {
		return impl.getUserStyleSheetURI();
	}

	public void addListenerForPageFormat(PropertyChangeListener listener) {
		impl.addListenerForPageFormat(listener);
	}

	public String getXMLParserClassName() {
		return impl.getXMLParserClassName();
	}

	public List<PrintService> getPrintServices() {
		return impl.getPrintServices();
	}

	public PrintService getPrintService() {
		return impl.getPrintService();
	}

	public String getMedia() {
		return impl.getMedia();
	}

	public void setPrintService(PrintService printService) {
		impl.setPrintService(printService);
	}

	public void addListenerForPrintService(PropertyChangeListener listener) {
		impl.addListenerForPrintService(listener);
	}

	public List<Page> getPages() {
		return impl.getPages();
	}

	public void addListenerForPages(PropertyChangeListener listener) {
		impl.addListenerForPages(listener);
	}

	public boolean supportExtension(String s) {
		return impl.supportExtension(s);
	}

	public void handleElement(Element elt, Object data) {
		impl.handleElement(elt, data);
	}

	public ScriptSecurity getScriptSecurity(String scriptType,
			ParsedURL scriptURL, ParsedURL docURL) {
		return impl.getScriptSecurity(scriptType, scriptURL, docURL);
	}

	public void checkLoadScript(String scriptType, ParsedURL scriptURL,
			ParsedURL docURL) throws SecurityException {
		impl.checkLoadScript(scriptType, scriptURL, docURL);
	}

	public ExternalResourceSecurity getExternalResourceSecurity(
			ParsedURL resourceURL, ParsedURL docURL) {
		return impl.getExternalResourceSecurity(resourceURL, docURL);
	}

	public void checkLoadExternalResource(ParsedURL resourceURL,
			ParsedURL docURL) throws SecurityException {
		impl.checkLoadExternalResource(resourceURL, docURL);
	}

	public SVGDocument getBrokenLinkDocument(Element arg0, String arg1,
			String arg2) {
		return impl.getBrokenLinkDocument(arg0, arg1, arg2);
	}

	public float getBolderFontWeight(float f) {
		return impl.getBolderFontWeight(f);
	}

	public String getAlternateStyleSheet() {
		return impl.getAlternateStyleSheet();
	}

	public void openLink(final SVGAElement arg0) {
		executeSynchronously(new Runnable() {
			public void run() {
				impl.openLink(arg0);
			}
		});
	}

	public void loadDocument(final URI uri) {
		executeSynchronously(new Runnable() {
			public void run() {
				impl.loadDocument(uri);
			}
		});
	}
	
	public void loadDocument(final URLConnection conn, final RequestBodySender sender) {
		executeSynchronously(new Runnable() {
			public void run() {
				impl.loadDocument(conn, sender);
			}
		});
	}

	@Override
	public List<TicketFormat> getTicketFormats() {
		return impl.getTicketFormats();
	}

	@Override
	public TicketFormat getTicketFormat() {
		return impl.getTicketFormat();
	}

	@Override
	public void setTicketFormat(final TicketFormat ticketFormat) {
		executeSynchronously(new Runnable() {
			public void run() {
				impl.setTicketFormat(ticketFormat);
			}
		});
	}

	@Override
	public void filterByOrderId(final Integer orderId) {
		executeSynchronously(new Runnable() {
			public void run() {
				impl.filterByOrderId(orderId);
			}
		});
	}

	@Override
	public void addListenerForTicketFormat(PropertyChangeListener listener) {
		impl.addListenerForTicketFormat(listener);
	}

	private void executeSynchronously(Runnable runnable) {
		try {
			executor.executeSynchronously(runnable);
		} catch (RuntimeException e) {
			throw e;
		} catch (Exception e) {
			throw new ApplicationException(e);
		}
	}
	
	public void dispose() {
		executor.terminate();
	}
	
	public AppAppletService(AppAppletServiceImpl impl) {
		this.impl = impl;
		executor = new SerializingExecutor(impl.getApplet());
	}
}