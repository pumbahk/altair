package jp.ticketstar.ticketing.printing.svg;

import org.apache.batik.dom.svg.SAXSVGDocumentFactory;
import org.apache.batik.dom.svg.SVGDOMImplementation;
import org.w3c.dom.DOMImplementation;

public class OurSAXSVGDocumentFactory extends SAXSVGDocumentFactory {

	public OurSAXSVGDocumentFactory(String parser) {
		super(parser);
	}

	public OurSAXSVGDocumentFactory(String parser, boolean dd) {
		super(parser, dd);
	}

    public DOMImplementation getDOMImplementation(String ver) {
        if (ver == null || ver.length() == 0
                || ver.equals("1.0") || ver.equals("1.1")) {
            return SVGDOMImplementation.getDOMImplementation();
        } else if (ver.equals("1.2")) {
            return ExtendedSVG12DOMImplementation.getDOMImplementation();
        }
        throw new RuntimeException("Unsupport SVG version '" + ver + "'");
    }
}
