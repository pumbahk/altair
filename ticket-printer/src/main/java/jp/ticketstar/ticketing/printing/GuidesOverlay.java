package jp.ticketstar.ticketing.printing;

import java.awt.BasicStroke;
import java.awt.Color;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.geom.Dimension2D;
import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.lang.ref.WeakReference;
import org.apache.batik.swing.gvt.Overlay;

public class GuidesOverlay implements Overlay {
	double[] horizontalGuides;
	double[] verticalGuides;
	Dimension2D size;
	
	static class PageFormatChangeListener implements PropertyChangeListener {
		final WeakReference<GuidesOverlay> outer;

		PageFormatChangeListener(GuidesOverlay outer) {
			this.outer = new WeakReference<GuidesOverlay>(outer);
		}

		public void propertyChange(PropertyChangeEvent evt) {
			if (evt.getPropertyName().equals("pageFormat")) {
				final OurPageFormat pageFormat = (OurPageFormat)evt.getNewValue();
				if (pageFormat != null) {
					outer.get().setGuides(
						pageFormat.getHorizontalGuides(),
						pageFormat.getVerticalGuides());
				} else {
					outer.get().setGuides(null, null);
				}
			} else if (evt.getPropertyName().equals("ticketSetModel")) {
				final TicketSetModel ticketSetModel = (TicketSetModel)evt.getNewValue();
				outer.get().setDocumentSize(ticketSetModel.getBridgeContext().getDocumentSize());
			}
		}
	}

	private void setGuides(double[] horizontalGuides, double[] verticalGuides) {
		this.horizontalGuides = horizontalGuides;
		this.verticalGuides = verticalGuides;
	}

	private void setDocumentSize(Dimension2D size) {
		this.size = (Dimension2D)size.clone();
	}
	
	public GuidesOverlay(AppWindowModel model) {
		model.addPropertyChangeListener(new PageFormatChangeListener(this));
		if (model.getPageFormat() != null)
			setGuides(model.getPageFormat().getHorizontalGuides(), model.getPageFormat().getVerticalGuides());
		if (model.getTicketSetModel() != null)
			setDocumentSize(model.getTicketSetModel().getBridgeContext().getDocumentSize());
	}

	public void paint(Graphics _g) {
		Graphics2D g = (Graphics2D)_g;
		g.setColor(Color.BLACK);
		g.setStroke(new BasicStroke(
			1.f, BasicStroke.CAP_BUTT,
	        BasicStroke.JOIN_MITER, 2.f, new float[] { 2.f }, 0.f));	
		if (verticalGuides != null) {
			for (double x: verticalGuides) {
				int _x = (int)UnitUtils.pointToPixel(x);
				g.drawLine(_x, 0, _x, (int)size.getHeight());
			}
		}
		if (horizontalGuides != null) {
			for (double y: horizontalGuides) {
				int _y = (int)UnitUtils.pointToPixel(y);
				g.drawLine(0, _y, (int)size.getWidth(), _y);
			}
		}
	}
}
