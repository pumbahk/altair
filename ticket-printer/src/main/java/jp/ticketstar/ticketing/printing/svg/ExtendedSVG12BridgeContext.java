package jp.ticketstar.ticketing.printing.svg;

import java.util.Collections;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.ListIterator;

import org.apache.batik.dom.svg.SVGOMDocument;
import org.apache.batik.bridge.BridgeContext;
import org.apache.batik.bridge.BridgeExtension;
import org.apache.batik.bridge.DocumentLoader;
import org.apache.batik.bridge.SVGBridgeExtension;
import org.apache.batik.bridge.UserAgent;
import org.apache.batik.bridge.svg12.SVG12BridgeContext;
import org.apache.batik.bridge.svg12.SVG12BridgeExtension;
import org.apache.batik.script.InterpreterPool;
import org.apache.batik.util.SVGConstants;
import org.w3c.dom.Document;
import org.w3c.dom.Element;

class ExtendedSVG12BridgeExtension extends SVG12BridgeExtension {
    public float getPriority() { return 0f; }

	@SuppressWarnings("unchecked")
	public Iterator<String> getImplementedExtensions() {
        return Collections.EMPTY_LIST.iterator();
    }

    public String getAuthor() {
        return "Proprietary, at the moment.";
    }

    public String getContactAddress() {
        return "moriyoshi@ticketstar.jp";
    }

    public String getURL() {
        return "http://ticketstar.jp/";
    }

    public String getDescription() {
        return "Extension to SVG 1.2 tags";
    }

    @Override
    public void registerTags(BridgeContext ctx) {
        super.registerTags(ctx);

        ctx.putBridge(new SVGPageElementBridge());
        ctx.putBridge(new SVGPageSetElementBridge());
    }
}

public class ExtendedSVG12BridgeContext extends SVG12BridgeContext {
	@SuppressWarnings("unchecked")
	@Override
    public List<BridgeExtension> getBridgeExtensions(Document doc) {
        Element root = ((SVGOMDocument)doc).getRootElement();
        String ver = root.getAttributeNS
            (null, SVGConstants.SVG_VERSION_ATTRIBUTE);
        BridgeExtension svgBE;
        if ((ver.length()==0) || ver.equals("1.0") || ver.equals("1.1"))
            svgBE = new SVGBridgeExtension();
        else
            svgBE = new ExtendedSVG12BridgeExtension();

        float priority = svgBE.getPriority();
        extensions = new LinkedList<BridgeExtension>(getGlobalBridgeExtensions());

        ListIterator<BridgeExtension> li = extensions.listIterator();
        for (;;) {
            if (!li.hasNext()) {
                li.add(svgBE);
                break;
            }
            BridgeExtension lbe = (BridgeExtension)li.next();
            if (lbe.getPriority() > priority) {
                li.previous();
                li.add(svgBE);
                break;
            }
        }

        return extensions;
    }
    
	public ExtendedSVG12BridgeContext(UserAgent userAgent,
			InterpreterPool interpreterPool, DocumentLoader documentLoader) {
		super(userAgent, interpreterPool, documentLoader);
	}

	public ExtendedSVG12BridgeContext(UserAgent userAgent, DocumentLoader loader) {
		super(userAgent, loader);
	}

	public ExtendedSVG12BridgeContext(UserAgent userAgent) {
		super(userAgent);
	}
}
