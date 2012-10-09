package jp.ticketstar.ticketing;

import java.awt.geom.Dimension2D;

public class DDimension2D extends Dimension2D implements Cloneable {
	double width;
	double height;

	public Dimension2D clone() {
		return new DDimension2D(width, height);
	}
	
	public DDimension2D() {
		this(0, 0);
	}
	
	public DDimension2D(double width, double height) {
		this.width = width;
		this.height = height;
	}
	
	@Override
	public double getWidth() {
		return width;
	}

	@Override
	public double getHeight() {
		return height;
	}

	@Override
	public void setSize(double width, double height) {
		this.width = width;
		this.height = height;
	}
}
