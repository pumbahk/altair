package jp.ticketstar.ticketing.printing;

import java.awt.print.PageFormat;

public class OurPageFormat extends PageFormat {
	String name;
	double[] horizontalGuides;
	double[] verticalGuides;
	
	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
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
