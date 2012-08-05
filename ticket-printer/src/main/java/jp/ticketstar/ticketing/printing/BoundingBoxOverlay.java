package jp.ticketstar.ticketing.printing;

import java.awt.BasicStroke;
import java.awt.Color;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.geom.Dimension2D;
import java.lang.ref.WeakReference;
import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import org.apache.batik.swing.gvt.Overlay;

public class BoundingBoxOverlay implements Overlay {
	Dimension2D pageSize;
	Dimension2D documentSize;
	
	static class PageFormatChangeListener implements PropertyChangeListener {
		final WeakReference<BoundingBoxOverlay> outer;

		PageFormatChangeListener(BoundingBoxOverlay outer) {
			this.outer = new WeakReference<BoundingBoxOverlay>(outer);
		}

		public void propertyChange(PropertyChangeEvent evt) {
			if (evt.getPropertyName().equals("pageFormat")) {
				final OurPageFormat pageFormat = (OurPageFormat)evt.getNewValue();
				if (pageFormat != null) {
					outer.get().setPageSize(
						UnitUtils.pointToPixel(new DDimension2D(
							pageFormat.getWidth(),
							pageFormat.getHeight())));
				} else {
					outer.get().setPageSize(null);
				}
			} else if (evt.getPropertyName().equals("ticketSetModel")) {
				final TicketSetModel ticketSetModel = (TicketSetModel)evt.getNewValue();
				outer.get().setDocumentSize(ticketSetModel.getBridgeContext().getDocumentSize());
			}
		}
	}

	private void setPageSize(Dimension2D size) {
		this.pageSize = size != null ? (Dimension2D)size.clone(): null;
	}
	
	private void setDocumentSize(Dimension2D size) {
		this.documentSize = size != null ? (Dimension2D)size.clone(): null;
	}
	
	public BoundingBoxOverlay(AppWindowModel model) {
		model.addPropertyChangeListener(new PageFormatChangeListener(this));
		if (model.getPageFormat() != null)
			setPageSize(new DDimension2D(model.getPageFormat().getWidth(), model.getPageFormat().getHeight()));
		if (model.getTicketSetModel() != null)
			setDocumentSize(model.getTicketSetModel().getBridgeContext().getDocumentSize());
	}

	static double pointToPixel(double point) {
		return point * 90 / 72;
	}
	
	public void paint(Graphics _g) {
		Graphics2D g = (Graphics2D)_g;
		g.setColor(Color.BLACK);
		g.setStroke(new BasicStroke());
		if (pageSize != null)
			g.drawRect(0, 0, (int)pageSize.getWidth(), (int)pageSize.getHeight());
		if (documentSize != null)
			g.drawRect(0, 0, (int)documentSize.getWidth(), (int)documentSize.getHeight());
	}
}
