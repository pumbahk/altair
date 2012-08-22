package jp.ticketstar.ticketing.printing;

import java.beans.PropertyChangeListener;
import java.beans.PropertyChangeSupport;
import java.util.Arrays;
import java.util.Iterator;
import java.util.NoSuchElementException;

import jp.ticketstar.ticketing.printing.svg.ExtendedSVG12BridgeContext;
import jp.ticketstar.ticketing.printing.svg.ExtendedSVG12OMDocument;
import jp.ticketstar.ticketing.printing.svg.SVGOMPageElement;
import jp.ticketstar.ticketing.printing.svg.SVGOMPageSetElement;

import org.apache.batik.bridge.GVTBuilder;
import org.apache.batik.dom.AbstractElement;
import org.apache.batik.dom.svg.SVGOMElement;
import org.apache.batik.dom.svg.SVGOMTitleElement;
import org.apache.batik.gvt.CompositeGraphicsNode;
import org.apache.batik.gvt.GraphicsNode;
import org.w3c.dom.Node;

class PageElementIterator implements Iterator<SVGOMPageElement> {
	AbstractElement current;
	
	public PageElementIterator(SVGOMPageSetElement pageSet) {
		this.current = (AbstractElement) pageSet.getFirstElementChild();
		advance();
	}

	public boolean hasNext() {
		return current != null;
	}

	void advance() {
		while (current != null && !(current instanceof SVGOMPageElement))
			current = (AbstractElement)current.getNextElementSibling();
	}

	public SVGOMPageElement next() {
		if (current == null)
			throw new NoSuchElementException();
		final SVGOMPageElement retval = (SVGOMPageElement)current;
		current = (AbstractElement)current.getNextElementSibling();
		advance();
		return retval;
	}

	public void remove() {
		throw new UnsupportedOperationException();
	}
}

public class TicketSetModel {
	PropertyChangeSupport propertyChangeSupport = new PropertyChangeSupport(this);
	ExtendedSVG12OMDocument svg;
	ExtendedSVG12BridgeContext bridgeContext;
	SVGOMPageSetElement pageSetElement;
	Tickets tickets;
	
	public Tickets getTickets() {
		return tickets;
	}

	public void addPropertyChangeListener(PropertyChangeListener listener) {
		propertyChangeSupport.addPropertyChangeListener(listener);
	}

	public void addPropertyChangeListener(String propertyName,
			PropertyChangeListener listener) {
		propertyChangeSupport.addPropertyChangeListener(propertyName, listener);
	}

	public PropertyChangeListener[] getPropertyChangeListeners() {
		return propertyChangeSupport.getPropertyChangeListeners();
	}

	public PropertyChangeListener[] getPropertyChangeListeners(
			String propertyName) {
		return propertyChangeSupport.getPropertyChangeListeners(propertyName);
	}

	public boolean hasListeners(String propertyName) {
		return propertyChangeSupport.hasListeners(propertyName);
	}

	public void removePropertyChangeListener(PropertyChangeListener listener) {
		propertyChangeSupport.removePropertyChangeListener(listener);
	}

	public void removePropertyChangeListener(String propertyName,
			PropertyChangeListener listener) {
		propertyChangeSupport.removePropertyChangeListener(propertyName,
				listener);
	}

	public SVGOMPageSetElement findPageSetElement(ExtendedSVG12OMDocument svg) {
		SVGOMPageSetElement pageSetElement = null;
		for (AbstractElement e = (AbstractElement)((AbstractElement)svg.getRootElement()).getFirstElementChild();
				e != null; e = (AbstractElement)e.getNextElementSibling()) {
			if (e instanceof SVGOMPageSetElement) {
				if (pageSetElement != null)
					throw new RuntimeException("SVG document must contain only one <pageSet> element.");
				pageSetElement = (SVGOMPageSetElement)e;
			}
		}
		if (pageSetElement == null)
			throw new RuntimeException("SVG document does not contain any <pageSet> element.");
		return pageSetElement;
	}

	public ExtendedSVG12BridgeContext getBridgeContext() {
		return bridgeContext;
	}

	private static String findTitle(SVGOMElement elem) {
		for (Node n = elem.getFirstChild(); n != null; n = n.getNextSibling()) {
			if (n instanceof SVGOMTitleElement) {
				return n.getTextContent();
			}
		}
		return null;
	}

	public GraphicsNode buildGVTNodeFromPage(SVGOMPageElement page) {
		return null;
	}

	private static void dumpGvtNode(GraphicsNode node, int indent) {
		StringBuffer buf = new StringBuffer();
		char[] spaces = new char[indent * 2];
		Arrays.fill(spaces, ' ');
		buf.append(spaces);
		buf.append(node.getClass().getSimpleName());
		System.err.println(buf);
		if (node instanceof CompositeGraphicsNode) {
			for (Object _node: ((CompositeGraphicsNode)node).getChildren())
				dumpGvtNode((GraphicsNode)_node, indent + 1);
		}
	}

	private static void dumpGvtNode(GraphicsNode node) {
		dumpGvtNode(node, 0);
	}
	
	public TicketSetModel(ExtendedSVG12BridgeContext ctx, ExtendedSVG12OMDocument svg) {
		this.bridgeContext = ctx;
		this.svg = svg;
		this.pageSetElement = findPageSetElement(svg);
		int pageNumber = 1;
		GVTBuilder builder = new GVTBuilder();
		final Tickets tickets = new Tickets();
		builder.build(ctx, svg);
		for (Iterator<SVGOMPageElement> i = new PageElementIterator(pageSetElement);
				i.hasNext(); pageNumber++) {
			if (pageNumber > 1000)
				throw new RuntimeException("Too many pages!");
			SVGOMPageElement page = i.next();
			String title = findTitle(page);
			dumpGvtNode(ctx.getGraphicsNode(page));
			tickets.add(
				new Ticket(
					title == null ?
							Integer.toString(pageNumber):
							String.format("%s (%d)", title, pageNumber),
					ctx.getGraphicsNode(page)));
		}
		this.tickets = tickets;
	}
}