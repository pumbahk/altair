package jp.ticketstar.ticketing.qrreader;

import org.apache.batik.bridge.BridgeContext;
import org.apache.batik.dom.svg.SVGOMDocument;

public interface BridgeContextFactory {
	public BridgeContext createBridgeContext(SVGOMDocument doc);
}
