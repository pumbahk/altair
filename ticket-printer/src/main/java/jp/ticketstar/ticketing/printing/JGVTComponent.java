package jp.ticketstar.ticketing.printing;

import java.awt.Color;
import java.awt.Graphics2D;
import java.awt.geom.AffineTransform;

import jp.ticketstar.ticketing.gvt.BasicJGVTComponent;

public class JGVTComponent extends BasicJGVTComponent {
	private static final long serialVersionUID = 1L;
	private OurPageFormat pageFormat;

	void drawPageRect(Graphics2D g2d) {
		if (pageFormat == null)
			return;
        g2d.setColor(Color.BLACK);
        final int width = (int)UnitUtils.pointToPixel(pageFormat.getWidth()),
        	      height = (int)UnitUtils.pointToPixel((int)pageFormat.getHeight());
        g2d.drawRect(0, 0, width, height);
        g2d.drawLine(2, height + 1, width + 1, height + 1);
        g2d.drawLine(width + 1, 2, width + 1, height + 1);
	}

    protected void beforeRender(Graphics2D g2d) {
        drawPageRect(g2d);

        g2d.transform(new AffineTransform(1, 0, 0, 1,
                pageFormat == null ? 0: UnitUtils.pointToPixel(pageFormat.getImageableX()),
                pageFormat == null ? 0: UnitUtils.pointToPixel(pageFormat.getImageableY())));
    }

	public JGVTComponent() {
		super();
	}
	
	public JGVTComponent(boolean eventsEnabled, boolean selectableText) {
		super(eventsEnabled, selectableText);
	}

	public OurPageFormat getPageFormat() {
		return pageFormat;
	}

	public void setPageFormat(OurPageFormat pageFormat) {
		this.pageFormat = pageFormat;
	}
}
