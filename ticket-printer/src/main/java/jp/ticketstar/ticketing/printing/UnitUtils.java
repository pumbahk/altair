package jp.ticketstar.ticketing.printing;

import java.awt.geom.Dimension2D;
import java.awt.geom.Point2D;

public class UnitUtils {
	public static double pointToPixel(double point) {
		return point * 90 / 72;
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
}
