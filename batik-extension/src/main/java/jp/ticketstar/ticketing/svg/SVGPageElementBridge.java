package jp.ticketstar.ticketing.svg;

import org.apache.batik.bridge.AbstractGraphicsNodeBridge;
import org.apache.batik.bridge.BridgeContext;
import org.apache.batik.gvt.CompositeGraphicsNode;
import org.apache.batik.gvt.GraphicsNode;
import org.w3c.dom.Element;

public class SVGPageElementBridge extends AbstractGraphicsNodeBridge {
	public boolean isComposite() {
		return true;
	}

	public String getLocalName() {
		return ExtendedSVG12Constants.SVG_PAGE_TAG;
	}

	@Override
	protected GraphicsNode instantiateGraphicsNode() {
		return new CompositeGraphicsNode();
	}

	@Override
	public GraphicsNode createGraphicsNode(BridgeContext ctx, Element e) {
		final GraphicsNode retval = instantiateGraphicsNode();
		associateSVGContext(ctx, e, retval);
		ctx.bind(e, retval);
		return retval;
	}
}
