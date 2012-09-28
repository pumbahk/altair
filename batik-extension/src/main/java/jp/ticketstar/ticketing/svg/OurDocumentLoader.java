package jp.ticketstar.ticketing.svg;

import org.apache.batik.bridge.DocumentLoader;
import org.apache.batik.bridge.UserAgent;

public class OurDocumentLoader extends DocumentLoader {
    public OurDocumentLoader(UserAgent userAgent) {
    	super(userAgent);
        documentFactory = new OurSAXSVGDocumentFactory(userAgent.getXMLParserClassName(), true);
        documentFactory.setValidating(userAgent.isXMLParserValidating());
    }
}
