package jp.ticketstar.ticketing.qrreader;

import java.io.IOException;
import java.io.StringReader;
import java.io.StringWriter;

import org.apache.batik.dom.svg.SAXSVGDocumentFactory;
import org.apache.batik.util.XMLResourceDescriptor;
import org.w3c.dom.svg.SVGDocument;

import com.github.mustachejava.Mustache;

public class MustacheTicketTemplate extends AbstractTicketTemplate {
	final Mustache mustache;
	
	public MustacheTicketTemplate(int id, String name, TicketFormat ticketFormat, Mustache mustache) {
		super(id, name, ticketFormat);
		this.mustache = mustache;
	}

	public Mustache getMustache() {
		return mustache;
	}
	
	public SVGDocument buildSVGDocument(Ticket ticket) throws IOException {
		final StringWriter writer = new StringWriter();
		mustache.execute(writer, ticket.getData());
		System.out.println(writer.toString());
		final SAXSVGDocumentFactory documentFactory = new SAXSVGDocumentFactory(
			XMLResourceDescriptor.getXMLParserClassName(), true);
		return documentFactory.createSVGDocument(
				"urn:ticketstar:ticket:" + ticket.getOrderedProductItemId(),
				new StringReader(writer.toString()));
	}
}
