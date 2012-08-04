package jp.ticketstar.ticketing.printing.svg;

import org.apache.batik.dom.AbstractDocument;
import org.apache.batik.dom.svg.SVGOMDocument;
import org.apache.batik.dom.svg12.SVG12DOMImplementation;
import org.apache.batik.dom.util.HashTable;
import org.w3c.dom.DOMException;
import org.w3c.dom.DOMImplementation;
import org.w3c.dom.Document;
import org.w3c.dom.DocumentType;
import org.w3c.dom.Element;

public class ExtendedSVG12DOMImplementation extends SVG12DOMImplementation {
	private static final long serialVersionUID = 1L;

	protected static HashTable extendedSvg12Factories = new HashTable(svg12Factories);

	static {
		extendedSvg12Factories.put(ExtendedSVG12Constants.SVG_PAGESET_TAG, new PageSetElementFactory());
		extendedSvg12Factories.put(ExtendedSVG12Constants.SVG_PAGE_TAG, new PageElementFactory());
	}

    public Document createDocument(String namespaceURI, String qualifiedName, DocumentType doctype) throws DOMException {
        SVGOMDocument result = new ExtendedSVG12OMDocument(doctype, this);
        result.setIsSVG12(true);
        if (qualifiedName != null)
            result.appendChild(result.createElementNS(namespaceURI, qualifiedName));
        return result;
    }

	protected static class PageSetElementFactory implements ElementFactory {
		public PageSetElementFactory() {}
	
		public Element create(String prefix, Document doc) {
			return new SVGOMPageSetElement(prefix, (AbstractDocument)doc);
		}
	}

	protected static class PageElementFactory implements ElementFactory {
		public PageElementFactory() {}
	
		public Element create(String prefix, Document doc) {
			return new SVGOMPageElement(prefix, (AbstractDocument)doc);
		}
	}

    protected static final DOMImplementation DOM_IMPLEMENTATION = new ExtendedSVG12DOMImplementation();

    public static DOMImplementation getDOMImplementation() {
        return DOM_IMPLEMENTATION;
    }

    public ExtendedSVG12DOMImplementation() {
    	factories = extendedSvg12Factories;
    }
}
