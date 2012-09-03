package jp.ticketstar.ticketing.printing;

import java.awt.geom.Dimension2D;
import java.awt.geom.Point2D;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class UnitUtils {
	static final Pattern regex = Pattern.compile("(-?[0-9]+(?:\\.[0-9]*)?|\\.[0-9]+)(pt|pc|mm|cm|in|px)?");
		
	public static double pointToPixel(double point) {
		return point * 90 / 72;
	}

	public static double picaToPoint(double pica) {
		return pica * 12;
	}

	public static double mmToPoint(double mm) {
	    return mm * 72 / 25.4;
	}

	public static double cmToPoint(double cm)  {
		return cm * 72 / 2.54;
	}

	public static double pixelToPoint(double px) {
		return px * 72 / 90;
	}
	
	public static Point2D pointToPixel(Point2D point) {
		final Point2D retval = (Point2D)point.clone();
		retval.setLocation(
			pointToPixel(point.getX()),
			pointToPixel(point.getY()));
		return retval;
	}
	
	public static Dimension2D pointToPixel(Dimension2D point) {
		final Dimension2D retval = (Dimension2D)point.clone();
		retval.setSize(
			pointToPixel(point.getWidth()),
			pointToPixel(point.getHeight()));
		return retval;
	}

	public static double convertToPoint(double value, String unit) {
	    if (unit.equalsIgnoreCase("pt"))
	    	return value;
	    else if (unit.equalsIgnoreCase("pc"))
	    	return picaToPoint(value);
	    else if (unit.equalsIgnoreCase("mm"))
	    	return mmToPoint(value);
	    else if (unit.equalsIgnoreCase("cm"))
	    	return cmToPoint(value);
	    else if (unit.equalsIgnoreCase("px"))
		    return pixelToPoint(value);
	    throw new Error("Unsupported unit: " + unit);
	}

	public static double convertToPoint(String value) {
		final Matcher match = regex.matcher(value);
		if (!match.matches())
		    throw new ApplicationException("Invalid length / size specifier: " + value);
		return convertToPoint(Double.parseDouble(match.group(1)), match.group(2));
	}
}
