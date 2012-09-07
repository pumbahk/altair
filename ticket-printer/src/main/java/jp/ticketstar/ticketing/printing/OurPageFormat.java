package jp.ticketstar.ticketing.printing;

import java.awt.PageAttributes;
import java.awt.print.PageFormat;

public class OurPageFormat extends PageFormat {
	int id;
	String name;
	double[] horizontalGuides;
	double[] verticalGuides;
	PageAttributes.MediaType preferredMediaType;

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

	public PageAttributes.MediaType getPreferredMediaType() {
		return preferredMediaType;
	}

	public void setPreferredMediaType(PageAttributes.MediaType mediaType) {
		this.preferredMediaType = mediaType;
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
