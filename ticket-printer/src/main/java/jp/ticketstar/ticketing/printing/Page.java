package jp.ticketstar.ticketing.printing;

import org.apache.batik.gvt.GraphicsNode;

public class Page {
	final String name;
	final GraphicsNode graphics;
	
	public String getName() {
		return name;
	}

	public GraphicsNode getGraphics() {
		return graphics;
	}
	
	public Page(String name, GraphicsNode graphics) {
		this.name = name;
		this.graphics = graphics;
	}
}