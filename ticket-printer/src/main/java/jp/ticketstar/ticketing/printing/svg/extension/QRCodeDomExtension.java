package jp.ticketstar.ticketing.printing.svg.extension;

import org.apache.batik.dom.AbstractDocument;
import org.apache.batik.dom.DomExtension;
import org.apache.batik.dom.ExtensibleDOMImplementation;
import org.apache.batik.dom.ExtensibleDOMImplementation.ElementFactory;
import org.w3c.dom.Document;
import org.w3c.dom.Element;

public class QRCodeDomExtension implements DomExtension {

	static class QRCodeElementFactory implements ElementFactory {
		public Element create(String prefix, Document doc) {
			return new QRCodeElement(prefix, (AbstractDocument)doc);
		}
	}
	
	public float getPriority() {
		return 1.f;
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

	public void registerTags(ExtensibleDOMImplementation di) {
		di.registerCustomElementFactory(
				QRCodeExtensionConstants.TS_SVG_EXTENSION_NAMESPACE,
				QRCodeExtensionConstants.TS_QRCODE_TAG,
				new QRCodeElementFactory());
	}
}
