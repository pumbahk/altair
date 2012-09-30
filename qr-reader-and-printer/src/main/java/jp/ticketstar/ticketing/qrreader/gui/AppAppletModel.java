package jp.ticketstar.ticketing.qrreader.gui;

import java.awt.print.PrinterJob;
import java.beans.PropertyChangeListener;
import java.beans.PropertyChangeSupport;
import java.security.AccessController;
import java.security.PrivilegedAction;

import javax.print.PrintService;
import javax.swing.event.SwingPropertyChangeSupport;

import jp.ticketstar.ticketing.swing.GenericComboBoxModel;
import jp.ticketstar.ticketing.swing.GenericListModel;
import jp.ticketstar.ticketing.qrreader.AppModel;
import jp.ticketstar.ticketing.qrreader.Ticket;
import jp.ticketstar.ticketing.qrreader.TicketTemplate;

public class AppAppletModel implements AppModel {
	PropertyChangeSupport propertyChangeSupport = new SwingPropertyChangeSupport(this, true);
	PrintService printService = null;
	GenericComboBoxModel<PrintService> printServices;
	GenericListModel<Ticket> tickets;
	GenericListModel<TicketTemplate> ticketTemplates;
	TicketTemplate ticketTemplate;

	public AppAppletModel() {
		initialize();
	}

	public void initialize() {
		{
			final GenericComboBoxModel<PrintService> printServices = new GenericComboBoxModel<PrintService>();
			try {
				System.getSecurityManager().checkPrintJobAccess();
				AccessController.doPrivileged(new PrivilegedAction<Object>() {
					public Object run() {
				        for (PrintService service: PrinterJob.lookupPrintServices())
				        	printServices.add(service);
				        return null;
					}
				});	
			} catch (SecurityException e) {
				throw e;
			}
	        final GenericComboBoxModel<PrintService> prevPrintServices = this.printServices;
	        this.printServices = printServices;
			propertyChangeSupport.firePropertyChange("printServices", prevPrintServices, printServices);
		}
		{
			final PrintService prevPrintService = this.printService;
			this.printService = this.printServices.size() > 0 ? this.printServices.get(0): null;
			propertyChangeSupport.firePropertyChange("printService", prevPrintService, this.printService);
		}
		{
	        final GenericListModel<Ticket> prevTickets = this.tickets;
			this.tickets = new GenericListModel<Ticket>();
			propertyChangeSupport.firePropertyChange("tickets", prevTickets, this.tickets);
		}
	}
	
	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.qrreader.gui.IAppWindowModel#refresh()
	 */
	public void refresh() {
		propertyChangeSupport.firePropertyChange("printServices", null, printServices);
		propertyChangeSupport.firePropertyChange("printService", null, printService);
		propertyChangeSupport.firePropertyChange("tickets", null, tickets);
	}

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.qrreader.gui.IAppWindowModel#addPropertyChangeListener(java.beans.PropertyChangeListener)
	 */
	public void addPropertyChangeListener(PropertyChangeListener arg0) {
		propertyChangeSupport.addPropertyChangeListener(arg0);
	}

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.qrreader.gui.IAppWindowModel#addPropertyChangeListener(java.lang.String, java.beans.PropertyChangeListener)
	 */
	public void addPropertyChangeListener(String arg0,
			PropertyChangeListener arg1) {
		propertyChangeSupport.addPropertyChangeListener(arg0, arg1);
	}

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.qrreader.gui.IAppWindowModel#getPropertyChangeListeners()
	 */
	public PropertyChangeListener[] getPropertyChangeListeners() {
		return propertyChangeSupport.getPropertyChangeListeners();
	}

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.qrreader.gui.IAppWindowModel#getPropertyChangeListeners(java.lang.String)
	 */
	public PropertyChangeListener[] getPropertyChangeListeners(String arg0) {
		return propertyChangeSupport.getPropertyChangeListeners(arg0);
	}

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.qrreader.gui.IAppWindowModel#hasListeners(java.lang.String)
	 */
	public boolean hasListeners(String arg0) {
		return propertyChangeSupport.hasListeners(arg0);
	}

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.qrreader.gui.IAppWindowModel#removePropertyChangeListener(java.beans.PropertyChangeListener)
	 */
	public void removePropertyChangeListener(PropertyChangeListener arg0) {
		propertyChangeSupport.removePropertyChangeListener(arg0);
	}

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.qrreader.gui.IAppWindowModel#removePropertyChangeListener(java.lang.String, java.beans.PropertyChangeListener)
	 */
	public void removePropertyChangeListener(String arg0,
			PropertyChangeListener arg1) {
		propertyChangeSupport.removePropertyChangeListener(arg0, arg1);
	}

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.qrreader.gui.IAppWindowModel#getPrintService()
	 */
	public PrintService getPrintService() {
		return printService;
	}

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.qrreader.gui.IAppWindowModel#setPrintService(javax.print.PrintService)
	 */
	public void setPrintService(PrintService printService) {
		final PrintService prevValue = this.printService;
		this.printService = printService;
		propertyChangeSupport.firePropertyChange("printService", prevValue, printService);
	}
	
	public GenericComboBoxModel<PrintService> getPrintServices() {
		return printServices;
	}

	@Override
	public GenericListModel<Ticket> getTickets() {
		return tickets;
	}

	@Override
	public GenericListModel<TicketTemplate> getTicketTemplates() {
		return ticketTemplates;
	}
	
	@Override
	public TicketTemplate getTicketTemplate() {
		return ticketTemplate;
	}

	@Override
	public void setTicketTemplate(TicketTemplate ticketTemplate) {
		final TicketTemplate prevValue = ticketTemplate;
		this.ticketTemplate = ticketTemplate;
		propertyChangeSupport.firePropertyChange("ticketTemplate", prevValue, ticketTemplate);
	}
}
