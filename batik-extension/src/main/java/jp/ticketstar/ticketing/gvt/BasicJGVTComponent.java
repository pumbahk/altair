package jp.ticketstar.ticketing.gvt;

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

public class BasicJGVTComponent extends AbstractJGVTComponent {
	private static final long serialVersionUID = 1L;

    protected void drawBackground(Graphics2D g2d) {
        final Rectangle visRect = getRenderRect();
        g2d.setComposite(AlphaComposite.SrcOver);
        g2d.setPaint(getBackground());
        g2d.fillRect(visRect.x,     visRect.y,
                     visRect.width, visRect.height);
    }

    protected void beforeRender(Graphics2D g2d) {
    }

	public void paintComponent(Graphics g) {
        final Graphics2D g2d = (Graphics2D)g;

        drawBackground(g2d);

        if (paintingTransform != null)
        	g2d.transform(paintingTransform);

        beforeRender(g2d);

        if (image != null) {
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
	
	public BasicJGVTComponent() {
		super();
	}
	
	public BasicJGVTComponent(boolean eventsEnabled, boolean selectableText) {
		super(eventsEnabled, selectableText);
	}
}
