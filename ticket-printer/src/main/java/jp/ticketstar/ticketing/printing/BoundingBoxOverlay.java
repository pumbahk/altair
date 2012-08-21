package jp.ticketstar.ticketing.printing;

import java.awt.BasicStroke;
import java.awt.Color;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.geom.Dimension2D;
import java.lang.ref.WeakReference;
import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;

import jp.ticketstar.ticketing.printing.gui.AppWindowModel;

import org.apache.batik.swing.gvt.Overlay;

public class BoundingBoxOverlay implements Overlay {
	Dimension2D documentSize;
	
	static class PageFormatChangeListener implements PropertyChangeListener {
		final WeakReference<BoundingBoxOverlay> outer;

		PageFormatChangeListener(BoundingBoxOverlay outer) {
			this.outer = new WeakReference<BoundingBoxOverlay>(outer);
		}

		public void propertyChange(PropertyChangeEvent evt) {
			if (evt.getPropertyName().equals("ticketSetModel")) {
				final TicketSetModel ticketSetModel = (TicketSetModel)evt.getNewValue();
				outer.get().setDocumentSize(ticketSetModel.getBridgeContext().getDocumentSize());
			}
		}
	}
	
	private void setDocumentSize(Dimension2D size) {
		this.documentSize = size != null ? (Dimension2D)size.clone(): null;
	}
	
	public BoundingBoxOverlay(AppWindowModel model) {
		model.addPropertyChangeListener(new PageFormatChangeListener(this));
		if (model.getTicketSetModel() != null)
			setDocumentSize(model.getTicketSetModel().getBridgeContext().getDocumentSize());
	}

	static double pointToPixel(double point) {
		return point * 90 / 72;
	}
	
	public void paint(Graphics _g) {
		Graphics2D g = (Graphics2D)_g;
		g.setColor(Color.LIGHT_GRAY);
		g.setStroke(new BasicStroke());
		if (documentSize != null)
			g.drawRect(0, 0, (int)documentSize.getWidth(), (int)documentSize.getHeight());
	}
}
