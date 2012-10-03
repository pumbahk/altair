package jp.ticketstar.ticketing.qrreader.gui;

import java.awt.Cursor;
import java.awt.Point;
import java.awt.geom.AffineTransform;
import java.awt.geom.Dimension2D;
import java.util.Map;

import jp.ticketstar.ticketing.qrreader.AppModel;
import jp.ticketstar.ticketing.qrreader.AppService;
import jp.ticketstar.ticketing.qrreader.CollectionUtils;
import jp.ticketstar.ticketing.qrreader.Ticket;
import jp.ticketstar.ticketing.qrreader.TicketImpl;
import jp.ticketstar.ticketing.qrreader.gui.liveconnect.LiveConnectUtils;
import netscape.javascript.JSObject;

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

public class AppAppletService extends AppService {
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
		try {
			final String seatId = (String)jsobj.getMember("seat_id").toString();
			final String orderedProductItemTokenId = (String)jsobj.getMember("ordered_product_item_token_id").toString();
			final String orderedProductItemId = (String)jsobj.getMember("ordered_product_item_id").toString();
			final String orderId = (String)jsobj.getMember("order_id").toString();
			final Map<String, String> data = CollectionUtils.stringValuedMap(LiveConnectUtils.jsObjectToMap((JSObject)jsobj.getMember("data"), false));
			return new TicketImpl(seatId, orderedProductItemTokenId, orderedProductItemId, orderId, data);
		} catch (RuntimeException e) {
			e.printStackTrace();
			throw e;
		}
	}

	public AppAppletService(AppApplet applet, AppModel model) {
		super(model);
		this.applet = applet;
	}
}