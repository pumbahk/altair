package jp.ticketstar.ticketing.qrreader;

import org.apache.batik.bridge.BridgeContext;
import org.apache.batik.bridge.UserAgent;
import org.apache.batik.bridge.svg12.SVG12BridgeContext;
import org.apache.batik.dom.svg.SVGOMDocument;

public class DefaultBridgeContextFactory implements BridgeContextFactory {
	final UserAgent userAgent;
	
	public DefaultBridgeContextFactory(UserAgent userAgent) {
		this.userAgent = userAgent;
	}
	
	public BridgeContext createBridgeContext(SVGOMDocument doc) {
		if (doc.isSVG12()) {
			return new SVG12BridgeContext(userAgent);
		} else {
			return new BridgeContext(userAgent);
		}
	}
}
