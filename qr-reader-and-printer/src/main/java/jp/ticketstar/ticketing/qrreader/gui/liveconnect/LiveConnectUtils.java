package jp.ticketstar.ticketing.qrreader.gui.liveconnect;

import netscape.javascript.JSObject;

import java.applet.Applet;
import java.util.Map;
import java.util.HashMap;

public class LiveConnectUtils {
	public static Object coerceToNative(final Applet applet, Object obj) {
		return coerceToNative(createPropertyIteratorJSFunction(JSObject.getWindow(applet)), obj);
	}
	
	public static Object coerceToNative(final JSObject propertyIteratorJSObject, Object obj) {
		if (obj == null) {
			return null;
		} else if (obj instanceof JSObject) {
			return jsObjectToMap(propertyIteratorJSObject, (JSObject)obj, true);
		} else {
			return obj;
		}
	}
	
	public static Map<String, Object> jsObjectToMap(JSObject jsobj, boolean recurse) {
		return jsObjectToMap(createPropertyIteratorJSFunction(jsobj), jsobj, recurse);
	}

	public static JSObject createPropertyIteratorJSFunction(JSObject jsobj) {
		return (JSObject)jsobj.eval("(function(obj) { var retval = []; for (var k in obj) { obj.hasOwnProperty(k) && retval.push(k); } return retval; })");	
	}
	
	public static Map<String, Object> jsObjectToMap(final JSObject propertyIteratorJSObject, JSObject jsobj, boolean recurse) {
		final Map<String, Object> retval = new HashMap<String, Object>();
		final JSObject members = (JSObject)propertyIteratorJSObject.call("call", new Object[] { null, jsobj });
		final int nmembers = ((Number)members.getMember("length")).intValue();
		for (int i = 0; i < nmembers; i++) {
			final String member = (String) members.getSlot(i);
			final Object value = jsobj.getMember(member);
			retval.put(member, recurse ? coerceToNative(propertyIteratorJSObject, value): value);
		}
		return retval;
	}
}
