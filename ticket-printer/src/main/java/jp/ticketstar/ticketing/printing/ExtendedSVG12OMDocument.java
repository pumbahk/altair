package jp.ticketstar.ticketing.printing;

import org.apache.batik.dom.svg12.SVG12OMDocument;
import org.w3c.dom.DOMImplementation;
import org.w3c.dom.DocumentType;
import org.w3c.dom.Node;

public class ExtendedSVG12OMDocument extends SVG12OMDocument {
	private static final long serialVersionUID = 1L;

	protected ExtendedSVG12OMDocument() {
    	super();
    }

    public ExtendedSVG12OMDocument(DocumentType dt, DOMImplementation impl) {
        super(dt, impl);
    }

    @Override
    protected Node newNode() {
        return new ExtendedSVG12OMDocument();
    }
}

