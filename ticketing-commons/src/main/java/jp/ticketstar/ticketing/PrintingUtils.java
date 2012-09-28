package jp.ticketstar.ticketing;

import java.awt.geom.Dimension2D;
import java.awt.geom.Rectangle2D;
import java.awt.print.Paper;

public class PrintingUtils {
    public static Paper buildPaper(Dimension2D size) {
    	return buildPaper(size, NESW.ZERO);
    }

    public static Paper buildPaper(Dimension2D size, NESW margin) {
        final Paper retval = new Paper();
        retval.setSize(size.getWidth(), size.getHeight());
        retval.setImageableArea(
        		margin.getLeft(),
        		margin.getTop(),
        		size.getWidth() - margin.getRight() - margin.getLeft(),
        		size.getHeight() - margin.getBottom() - margin.getTop());
        return retval;
    }

    public static Paper buildPaper(Dimension2D size, Rectangle2D imageableArea) {
        final Paper retval = new Paper();
        retval.setSize(size.getWidth(), size.getHeight());
        retval.setImageableArea(
        		imageableArea.getX(),
        		imageableArea.getY(),
        		imageableArea.getWidth(),
        		imageableArea.getHeight());
        return retval;
    }
}
