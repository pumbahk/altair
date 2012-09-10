package jp.ticketstar.ticketing.printing;

import java.util.Collection;
import java.util.Collections;

import org.apache.batik.gvt.GraphicsNode;

public class Page {
	final String name;
	final GraphicsNode graphics;
	final Collection<String> queueIds;
	
	public String getName() {
		return name;
	}

	public GraphicsNode getGraphics() {
		return graphics;
	}
	
	public Page(String name, GraphicsNode graphics, Collection<String> queueIds) {
		this.name = name;
		this.graphics = graphics;
		this.queueIds = Collections.unmodifiableCollection(queueIds);
	}

	public Collection<String> getQueueIds() {
		return queueIds;
	}
}