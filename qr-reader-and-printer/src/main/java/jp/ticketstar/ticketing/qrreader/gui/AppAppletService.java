package jp.ticketstar.ticketing.qrreader.gui;

import java.util.Map;

import jp.ticketstar.ticketing.qrreader.AppModel;
import jp.ticketstar.ticketing.qrreader.AppService;
import jp.ticketstar.ticketing.qrreader.CollectionUtils;
import jp.ticketstar.ticketing.qrreader.Ticket;
import jp.ticketstar.ticketing.qrreader.TicketImpl;
import jp.ticketstar.ticketing.qrreader.gui.liveconnect.LiveConnectUtils;

import netscape.javascript.JSObject;

import org.apache.batik.bridge.UserAgent;
import org.apache.batik.bridge.UserAgentAdapter;

public class AppAppletService extends AppService {
	private AppApplet applet;
	protected final UserAgent userAgent = new UserAgentAdapter() {
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