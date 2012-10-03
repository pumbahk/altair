package jp.ticketstar.ticketing.qrreader.gui.liveconnect;

import netscape.javascript.JSObject;
import java.util.Map;
import java.util.HashMap;

public class LiveConnectUtils {
	public static Object coerceToNative(Object obj) {
		if (obj == null) {
			return null;
		} else if (obj instanceof JSObject) {
			return jsObjectToMap((JSObject)obj, true);
		} else {
			return obj;
		}
	}
	
	public static Map<String, Object> jsObjectToMap(JSObject jsobj, boolean recurse) {
		final Map<String, Object> retval = new HashMap<String, Object>();
		final JSObject members = (JSObject)jsobj.eval("var retval = []; for (k in this) { this.hasOwnProperty(k) && retval.push(k); }; return retval;");
		final int nmembers = (int)(Integer)members.getMember("length");
		for (int i = 0; i < nmembers; i++) {
			final String member = (String) members.getSlot(i);
			final Object value = jsobj.getMember(member);
			retval.put(member, recurse ? coerceToNative(value): value);
		}
		return retval;
	}
}
