package jp.ticketstar.ticketing.qrreader.gui;

import java.io.IOException;
import java.net.URL;
import java.net.URLConnection;
import java.awt.Component;
import java.awt.Cursor;
import java.awt.Dimension;
import java.awt.Point;
import java.awt.geom.AffineTransform;
import java.awt.geom.Dimension2D;
import java.util.Map;

import javax.swing.DefaultListCellRenderer;
import javax.swing.JApplet;
import javax.swing.JLabel;
import javax.swing.JList;

import jp.ticketstar.ticketing.qrreader.AppService;
import jp.ticketstar.ticketing.ApplicationException;
import jp.ticketstar.ticketing.qrreader.AppModel;
import jp.ticketstar.ticketing.qrreader.CollectionUtils;
import jp.ticketstar.ticketing.qrreader.Ticket;
import jp.ticketstar.ticketing.qrreader.TicketFormat;
import jp.ticketstar.ticketing.qrreader.TicketImpl;
import jp.ticketstar.ticketing.qrreader.gui.liveconnect.LiveConnectUtils;
import jp.ticketstar.ticketing.URLConnectionFactory;

import org.apache.batik.bridge.BridgeExtension;
import org.apache.batik.bridge.ExternalResourceSecurity;
import org.apache.batik.bridge.ScriptSecurity;
import org.apache.batik.bridge.UserAgent;
import org.apache.batik.gvt.event.EventDispatcher;
import org.apache.batik.gvt.text.Mark;
import org.apache.batik.util.ParsedURL;
import org.w3c.dom.Element;
import org.w3c.dom.svg.SVGAElement;
import org.w3c.dom.svg.SVGDocument;

import netscape.javascript.JSObject;

import com.github.mustachejava.DefaultMustacheFactory;
import com.github.mustachejava.MustacheFactory;
import com.google.gson.JsonElement;
import com.google.gson.JsonParser;

class AppAppletService extends AppService {
	private AppApplet applet;
	protected final UserAgent userAgent = new UserAgent() {
		@Override
		public EventDispatcher getEventDispatcher() {
			// TODO Auto-generated method stub
			return null;
		}
	
		@Override
		public Dimension2D getViewportSize() {
			// TODO Auto-generated method stub
			return null;
		}
	
		@Override
		public void displayError(Exception ex) {
			ex.printStackTrace(System.err);
		}
	
		@Override
		public void displayMessage(String message) {
	    	final JSObject window = JSObject.getWindow(applet);
	    	window.call("alert", new Object[] { message });
		}
	
		@Override
		public void showAlert(String message) {
	    	final JSObject window = JSObject.getWindow(applet);
	    	window.call("alert", new Object[] { message });
		}
	
		@Override
		public String showPrompt(String message) {
			// TODO Auto-generated method stub
			return null;
		}
	
		@Override
		public String showPrompt(String message, String defaultValue) {
			// TODO Auto-generated method stub
			return null;
		}
	
		@Override
		public boolean showConfirm(String message) {
			// TODO Auto-generated method stub
			return false;
		}
	
		@Override
		public float getPixelUnitToMillimeter() {
			// TODO Auto-generated method stub
			return 0;
		}
	
		@Override
		public float getPixelToMM() {
			// TODO Auto-generated method stub
			return 0;
		}
	
		@Override
		public float getMediumFontSize() {
			// TODO Auto-generated method stub
			return 0;
		}
	
		@Override
		public float getLighterFontWeight(float f) {
			// TODO Auto-generated method stub
			return 0;
		}
	
		@Override
		public float getBolderFontWeight(float f) {
			// TODO Auto-generated method stub
			return 0;
		}
	
		@Override
		public String getDefaultFontFamily() {
			// TODO Auto-generated method stub
			return null;
		}
	
		@Override
		public String getLanguages() {
			// TODO Auto-generated method stub
			return null;
		}
	
		@Override
		public String getUserStyleSheetURI() {
			// TODO Auto-generated method stub
			return null;
		}
	
		@Override
		public void openLink(SVGAElement elt) {
			// TODO Auto-generated method stub
			
		}
	
		@Override
		public void setSVGCursor(Cursor cursor) {
			// TODO Auto-generated method stub
			
		}
	
		@Override
		public void setTextSelection(Mark start, Mark end) {
			// TODO Auto-generated method stub
			
		}
	
		@Override
		public void deselectAll() {
			// TODO Auto-generated method stub
			
		}
	
		@Override
		public String getXMLParserClassName() {
			// TODO Auto-generated method stub
			return null;
		}
	
		@Override
		public boolean isXMLParserValidating() {
			// TODO Auto-generated method stub
			return false;
		}
	
		@Override
		public AffineTransform getTransform() {
			// TODO Auto-generated method stub
			return null;
		}
	
		@Override
		public void setTransform(AffineTransform at) {
			// TODO Auto-generated method stub
			
		}
	
		@Override
		public String getMedia() {
			// TODO Auto-generated method stub
			return null;
		}
	
		@Override
		public String getAlternateStyleSheet() {
			// TODO Auto-generated method stub
			return null;
		}
	
		@Override
		public Point getClientAreaLocationOnScreen() {
			// TODO Auto-generated method stub
			return null;
		}
	
		@Override
		public boolean hasFeature(String s) {
			// TODO Auto-generated method stub
			return false;
		}
	
		@Override
		public boolean supportExtension(String s) {
			// TODO Auto-generated method stub
			return false;
		}
	
		@Override
		public void registerExtension(BridgeExtension ext) {
			// TODO Auto-generated method stub
			
		}
	
		@Override
		public void handleElement(Element elt, Object data) {
			// TODO Auto-generated method stub
			
		}
	
		@Override
		public ScriptSecurity getScriptSecurity(String scriptType,
				ParsedURL scriptURL, ParsedURL docURL) {
			// TODO Auto-generated method stub
			return null;
		}
	
		@Override
		public void checkLoadScript(String scriptType, ParsedURL scriptURL,
				ParsedURL docURL) throws SecurityException {
			// TODO Auto-generated method stub
			
		}
	
		@Override
		public ExternalResourceSecurity getExternalResourceSecurity(
				ParsedURL resourceURL, ParsedURL docURL) {
			// TODO Auto-generated method stub
			return null;
		}
	
		@Override
		public void checkLoadExternalResource(ParsedURL resourceURL,
				ParsedURL docURL) throws SecurityException {
			// TODO Auto-generated method stub
			
		}
	
		@Override
		public SVGDocument getBrokenLinkDocument(Element e, String url,
				String message) {
			// TODO Auto-generated method stub
			return null;
		}
	};

	public Ticket createTicketFromJSObject(JSObject jsobj) {
		final String seatId = (String)jsobj.getMember("seat_id");
		final String orderedProductItemId = (String)jsobj.getMember("ordered_product_item_id");
		final String orderId = (String)jsobj.getMember("order_id");
		final Map<String, String> data = CollectionUtils.stringValuedMap(LiveConnectUtils.jsObjectToMap((JSObject)jsobj.getMember("data"), false));
		return new TicketImpl(seatId, orderedProductItemId, orderId, data);
	}
	
	public AppAppletService(AppApplet applet, AppModel model) {
		super(model);
		this.applet = applet;
	}
};

class TicketFormatCellRenderer extends DefaultListCellRenderer {
	private static final long serialVersionUID = 1L;

	@Override
	public Component getListCellRendererComponent(JList list, Object value, int index, boolean isSelected, boolean cellHasFocus) {
		JLabel label = (JLabel)super.getListCellRendererComponent(list, value, index, isSelected, cellHasFocus);
		if (value != null)
			label.setText(((TicketFormat)value).getName());
		return label;
	}
}

/**
 * Created with IntelliJ IDEA.
 * User: mistat
 * Date: 8/9/12
 * Time: 10:00 PM
 * To change this template use File | Settings | File Templates.
 */
public class AppApplet extends JApplet implements IAppWindow, URLConnectionFactory {
	private static final long serialVersionUID = 1L;

	protected final MustacheFactory mustacheFactory;

	public AppApplet() {
		setPreferredSize(new Dimension(2147483647, 2147483647));
		mustacheFactory = new DefaultMustacheFactory();
	}
	
	AppAppletService appService;
	AppAppletModel model;
	AppAppletConfiguration config;

	public void unbind() {
		if (model == null)
			return;
	}
	
	public void bind(AppModel model) {
		unbind();
		model.refresh();
		this.model = (AppAppletModel)model;
	}

	private AppAppletConfiguration getConfiguration() throws ApplicationException {
		final AppAppletConfiguration config = new AppAppletConfiguration();
		final String endpointsJson = getParameter("endpoints");
		if (endpointsJson == null)
			throw new ApplicationException("required parameter \"endpoints\" not specified");
		final String cookie = getParameter("cookie");
		if (cookie == null)
			throw new ApplicationException("required parameter \"cookie\" not specified");
		config.cookie = cookie;
		try {
			final JsonElement elem = new JsonParser().parse(endpointsJson);
			config.formatsUrl = new URL(getCodeBase(), elem.getAsJsonObject().get("formats").getAsString());
			config.peekUrl = new URL(getCodeBase(), elem.getAsJsonObject().get("peek").getAsString());
			config.dequeueUrl = new URL(getCodeBase(), elem.getAsJsonObject().get("dequeue").getAsString());
		} catch (Exception e) {
			throw new ApplicationException(e);
		}
		return config;
	}
	
	public URLConnection newURLConnection(final URL url) throws IOException {
		URLConnection conn = url.openConnection();
		conn.setRequestProperty("Cookie", config.cookie);
		conn.setUseCaches(false);
		conn.setAllowUserInteraction(true);
		return conn;
	}

	void populateModel() {
		final FormatLoader.LoaderResult result = new FormatLoader(this, mustacheFactory).fetchFormats(config);
		if (result.ticketTemplates.size() > 0) {
			model.getTicketTemplates().addAll(result.ticketTemplates);
			model.setTicketTemplate(result.ticketTemplates.get(0));
		}
	}

	public void init() {
		config = getConfiguration();
		model = new AppAppletModel();
    	appService = new AppAppletService(this, model);
		appService.setAppWindow(this);
		populateModel();
	}
}
