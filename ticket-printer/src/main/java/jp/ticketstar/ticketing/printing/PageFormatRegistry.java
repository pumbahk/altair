package jp.ticketstar.ticketing.printing;

import java.awt.geom.Dimension2D;
import java.awt.print.PageFormat;
import java.awt.print.Paper;

public class PageFormatRegistry {
    static double mmToPoint(double mm) {
        return mm / (25.4 / 72);
    }

    static Paper buildPaper(Dimension2D size) {
        final Paper retval = new Paper();
        retval.setSize(size.getWidth(), size.getHeight());
        retval.setImageableArea(0, 0, size.getWidth(), size.getHeight());
        return retval;
    }

    public static OurPageFormat buildPageFormatForRT() {
        final OurPageFormat retval = new OurPageFormat();
        retval.setName("楽天チケット");
        retval.setVerticalGuides(new double[] { mmToPoint(19.2), mmToPoint(148.1) });
        retval.setPaper(buildPaper(new DDimension2D(mmToPoint(65.04), mmToPoint(177.96))));
        retval.setOrientation(PageFormat.LANDSCAPE);
        return retval;
    }
}
