package jp.ticketstar.ticketing.printing.gui.liveconnect;

import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;

import netscape.javascript.JSObject;

public class JSObjectPropertyChangeListenerProxy implements PropertyChangeListener {
	final JSObject jsobj;
	
	public JSObjectPropertyChangeListenerProxy(JSObject jsobj) {
		this.jsobj = jsobj;
	}
	
	public void propertyChange(PropertyChangeEvent evt) {
		jsobj.call("call", new Object[] { null, evt });
	}
}
