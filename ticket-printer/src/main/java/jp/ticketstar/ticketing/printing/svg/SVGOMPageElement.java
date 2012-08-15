package jp.ticketstar.ticketing.printing.svg;

import org.apache.batik.dom.AbstractDocument;
import org.apache.batik.dom.svg.SVGGraphicsElement;
import org.w3c.dom.Node;

public class SVGOMPageElement extends SVGGraphicsElement {
	private static final long serialVersionUID = 1L;

	@Override
	protected Node newNode() {
		return new SVGOMPageElement();
	}

	@Override
	public String getLocalName() {
		return ExtendedSVG12Constants.SVG_PAGE_TAG;
	}
	
	public SVGOMPageElement() {}
	
	public SVGOMPageElement(String prefix, AbstractDocument owner) {
		super(prefix, owner);
	}
}
