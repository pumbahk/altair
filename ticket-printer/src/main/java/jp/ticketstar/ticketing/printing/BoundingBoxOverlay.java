package jp.ticketstar.ticketing.printing;

import java.awt.BasicStroke;
import java.awt.Color;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.geom.Rectangle2D;
import java.lang.ref.WeakReference;
import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;

import jp.ticketstar.ticketing.UnitUtils;


import org.apache.batik.swing.gvt.Overlay;

public class BoundingBoxOverlay implements Overlay {
	Rectangle2D imageableArea;
	
	static class PageFormatChangeListener implements PropertyChangeListener {
		final WeakReference<BoundingBoxOverlay> outer;

		PageFormatChangeListener(BoundingBoxOverlay outer) {
			this.outer = new WeakReference<BoundingBoxOverlay>(outer);
		}

		public void propertyChange(PropertyChangeEvent evt) {
			if (evt.getPropertyName().equals("pageFormat")) {
				final OurPageFormat pageFormat = ((AppModel)evt.getSource()).getPageFormat();
				outer.get().setImageableArea(
					pageFormat == null ? null:
						new Rectangle2D.Double(
							pageFormat.getImageableX(),
							pageFormat.getImageableY(),
							pageFormat.getImageableWidth(),
							pageFormat.getImageableHeight()));
			}
		}
	}
	
	private void setImageableArea(Rectangle2D rect) {
		this.imageableArea = rect != null ? (Rectangle2D)rect.clone(): null;
	}
	
	public BoundingBoxOverlay(AppModel model) {
		model.addPropertyChangeListener(new PageFormatChangeListener(this));
		if (model.getPageFormat() != null) {
			final OurPageFormat pageFormat = model.getPageFormat();
			setImageableArea(
				new Rectangle2D.Double(
					pageFormat.getImageableX(),
					pageFormat.getImageableY(),
					pageFormat.getImageableWidth(),
					pageFormat.getImageableHeight()));
		}
	}
	
	public void paint(Graphics _g) {
		if (imageableArea == null)
			return;
		Graphics2D g = (Graphics2D)_g;
		g.setColor(Color.LIGHT_GRAY);
		g.setStroke(new BasicStroke());
			g.drawRect(0, 0, (int)UnitUtils.pointToPixel(imageableArea.getWidth()), (int)UnitUtils.pointToPixel(imageableArea.getHeight()));
	}
}
