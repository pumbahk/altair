package jp.ticketstar.ticketing.svg;

import org.apache.batik.anim.dom.SVGStylableElement;
import org.apache.batik.dom.AbstractDocument;
import org.w3c.dom.Element;
import org.w3c.dom.Node;

public class SVGOMPageSetElement extends SVGStylableElement implements Element {
	private static final long serialVersionUID = 1L;

	@Override
	protected Node newNode() {
		return new SVGOMPageSetElement();
	}

	@Override
	public String getLocalName() {
		return ExtendedSVG12Constants.SVG_PAGESET_TAG;
	}

	public SVGOMPageSetElement() {}

	public SVGOMPageSetElement(String prefix, AbstractDocument owner) {
		super(prefix, owner);
	}
}
