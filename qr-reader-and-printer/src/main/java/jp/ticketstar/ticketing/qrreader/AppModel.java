package jp.ticketstar.ticketing.qrreader;

import java.beans.PropertyChangeListener;

import javax.print.PrintService;

import jp.ticketstar.ticketing.swing.GenericComboBoxModel;
import jp.ticketstar.ticketing.swing.GenericListModel;

public interface AppModel {
	public abstract void initialize();

	public abstract void refresh();

	public abstract void addPropertyChangeListener(PropertyChangeListener arg0);

	public abstract void addPropertyChangeListener(String arg0,
			PropertyChangeListener arg1);

	public abstract PropertyChangeListener[] getPropertyChangeListeners();

	public abstract PropertyChangeListener[] getPropertyChangeListeners(
			String arg0);

	public abstract boolean hasListeners(String arg0);

	public abstract void removePropertyChangeListener(
			PropertyChangeListener arg0);

	public abstract void removePropertyChangeListener(String arg0,
			PropertyChangeListener arg1);

	public abstract GenericListModel<Ticket> getTickets();

	public abstract PrintService getPrintService();

	public abstract void setPrintService(PrintService printService);

	public abstract GenericComboBoxModel<PrintService> getPrintServices();

	public abstract void setPageFormat(OurPageFormat pageFormat);

	public abstract OurPageFormat getPageFormat();
	
	public abstract GenericComboBoxModel<OurPageFormat> getPageFormats();

	public abstract GenericListModel<TicketTemplate> getTicketTemplates();
	
	public abstract void setTicketTemplate(TicketTemplate ticketTemplate);

	public abstract TicketTemplate getTicketTemplate();
}
