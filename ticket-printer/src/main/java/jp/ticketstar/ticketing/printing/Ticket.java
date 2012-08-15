package jp.ticketstar.ticketing.printing;

import org.apache.batik.gvt.GraphicsNode;

public class Ticket {
	final String name;
	final GraphicsNode graphics;
	
	public String getName() {
		return name;
	}

	public GraphicsNode getGraphics() {
		return graphics;
	}
	
	public Ticket(String name, GraphicsNode graphics) {
		this.name = name;
		this.graphics = graphics;
	}
}