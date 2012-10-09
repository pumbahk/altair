package jp.ticketstar.ticketing.svg.extension;

import java.util.Arrays;
import java.util.Collections;
import java.util.Iterator;

import org.apache.batik.bridge.BridgeContext;
import org.apache.batik.bridge.BridgeExtension;
import org.w3c.dom.Element;

public class QRCodeBridgeExtension implements BridgeExtension {
	public static final String[] implementedExtensions = {
		QRCodeExtensionConstants.TS_SVG_EXTENSION_NAMESPACE
	};
	public float getPriority() {
		return 1.f;
	}

	public Iterator<String> getImplementedExtensions() {
		return Collections.unmodifiableList(Arrays.asList(implementedExtensions)).iterator();
	}

	public String getAuthor() {
		return "TicketStar, Inc.";
	}

	public String getContactAddress() {
		return "dev@ticketstar.jp";
	}

	public String getURL() {
		return "http://github.com/ticketstar/";
	}

	public String getDescription() {
		return "TicketStar SVG Extensions";
	}

	public void registerTags(BridgeContext ctx) {
		ctx.putBridge(new QRCodeElementBridge());
	}

	public boolean isDynamicElement(Element e) {
		return false;
	}
}
