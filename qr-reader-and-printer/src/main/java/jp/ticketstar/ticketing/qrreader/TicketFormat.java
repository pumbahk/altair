package jp.ticketstar.ticketing.qrreader;

import java.awt.geom.Dimension2D;
import java.awt.geom.Rectangle2D;

public class TicketFormat {
	int id;
	String name;
	Dimension2D size;
	Rectangle2D[] printableAreas;
	double[] horizontalGuides;
	double[] verticalGuides;

	public int getId() {
		return id;
	}

	public void setId(int id) {
		this.id = id;
	}
	
	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
	}

	public Dimension2D getSize() {
		return size;
	}

	public void setSize(Dimension2D size) {
		this.size = size;
	}

	public Rectangle2D[] getPrintableAreas() {
		return printableAreas;
	}

	public void setPrintableAreas(Rectangle2D[] printableAreas) {
		this.printableAreas = printableAreas;
	}
	
	public double[] getHorizontalGuides() {
		return horizontalGuides;
	}

	public void setHorizontalGuides(double[] horizontalGuides) {
		this.horizontalGuides = horizontalGuides;
	}

	public double[] getVerticalGuides() {
		return verticalGuides;
	}

	public void setVerticalGuides(double[] verticalGuides) {
		this.verticalGuides = verticalGuides;
	}
}
