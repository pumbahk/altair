package jp.ticketstar.ticketing.printing;

import java.awt.AlphaComposite;
import java.awt.Color;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.Rectangle;
import java.awt.RenderingHints;
import java.awt.geom.AffineTransform;

import org.apache.batik.swing.gvt.AbstractJGVTComponent;
import org.apache.batik.swing.gvt.Overlay;

import java.util.Iterator;

public class JGVTComponent extends AbstractJGVTComponent {
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

	public void paintComponent(Graphics g) {
        final Graphics2D g2d = (Graphics2D)g;

        final Rectangle visRect = getRenderRect();
        g2d.setComposite(AlphaComposite.SrcOver);
        g2d.setPaint(getBackground());
        g2d.fillRect(visRect.x,     visRect.y,
                     visRect.width, visRect.height);

        if (paintingTransform != null)
        	g2d.transform(paintingTransform);
        
        drawPageRect(g2d);
        
        if (image != null) {
        	g2d.transform(new AffineTransform(1, 0, 0, 1,
        			pageFormat == null ? 0: pageFormat.getImageableX(),
        			pageFormat == null ? 0: pageFormat.getImageableY()));
            g2d.drawRenderedImage(image, null);
            g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING,
                                 RenderingHints.VALUE_ANTIALIAS_OFF);
            @SuppressWarnings("unchecked")
			final Iterator<Overlay> it = (Iterator<Overlay>)overlays.iterator();
            while (it.hasNext()) {
                it.next().paint(g);
            }
        }	
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
