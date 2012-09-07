package jp.ticketstar.ticketing.printing.gui;

import java.awt.print.PrinterJob;
import java.beans.PropertyChangeListener;
import java.beans.PropertyChangeSupport;

import javax.print.PrintService;
import javax.swing.event.SwingPropertyChangeSupport;

import jp.ticketstar.ticketing.printing.GenericComboBoxModel;
import jp.ticketstar.ticketing.printing.AppModel;
import jp.ticketstar.ticketing.printing.OurPageFormat;
import jp.ticketstar.ticketing.printing.PageSetModel;
import jp.ticketstar.ticketing.printing.TicketFormat;

public class AppAppletModel implements AppModel {
	PropertyChangeSupport propertyChangeSupport = new SwingPropertyChangeSupport(this, true);
	PageSetModel pageSetModel = null;
	PrintService printService = null;
	GenericComboBoxModel<PrintService> printServices;
	OurPageFormat pageFormat = null;
	GenericComboBoxModel<OurPageFormat> pageFormats;
	TicketFormat ticketFormat = null;
	GenericComboBoxModel<TicketFormat> ticketFormats;

	public AppAppletModel() {
		initialize();
	}

	public void initialize() {
		{
			final GenericComboBoxModel<PrintService> printServices = new GenericComboBoxModel<PrintService>();
	        for (PrintService service: PrinterJob.lookupPrintServices())
	        	printServices.add(service);
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
	        final GenericComboBoxModel<OurPageFormat> prevPageFormats = this.pageFormats;
			this.pageFormats = new GenericComboBoxModel<OurPageFormat>();
			propertyChangeSupport.firePropertyChange("pageFormats", prevPageFormats, this.pageFormats);
		}
		{
	        final GenericComboBoxModel<TicketFormat> prevPageFormats = this.ticketFormats;
			this.ticketFormats = new GenericComboBoxModel<TicketFormat>();
			propertyChangeSupport.firePropertyChange("ticketFormats", prevPageFormats, this.ticketFormats);
		}
		{
			final OurPageFormat prevPageFormat = this.pageFormat;
			this.pageFormat = this.pageFormats.size() > 0 ? this.pageFormats.get(0): null;
			propertyChangeSupport.firePropertyChange("pageFormat", prevPageFormat, pageFormat);
		}
	}
	
	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#refresh()
	 */
	public void refresh() {
		propertyChangeSupport.firePropertyChange("pageSetModel", null, pageSetModel);
		propertyChangeSupport.firePropertyChange("printServices", null, printServices);
		propertyChangeSupport.firePropertyChange("printService", null, printService);
		propertyChangeSupport.firePropertyChange("pageFormats", null, pageFormats);
		propertyChangeSupport.firePropertyChange("pageFormat", null, pageFormat);
		propertyChangeSupport.firePropertyChange("ticketFormats", null, ticketFormats);
		propertyChangeSupport.firePropertyChange("ticketFormat", null, ticketFormat);
	}

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#addPropertyChangeListener(java.beans.PropertyChangeListener)
	 */
	public void addPropertyChangeListener(PropertyChangeListener arg0) {
		propertyChangeSupport.addPropertyChangeListener(arg0);
	}

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#addPropertyChangeListener(java.lang.String, java.beans.PropertyChangeListener)
	 */
	public void addPropertyChangeListener(String arg0,
			PropertyChangeListener arg1) {
		propertyChangeSupport.addPropertyChangeListener(arg0, arg1);
	}

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#getPropertyChangeListeners()
	 */
	public PropertyChangeListener[] getPropertyChangeListeners() {
		return propertyChangeSupport.getPropertyChangeListeners();
	}

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#getPropertyChangeListeners(java.lang.String)
	 */
	public PropertyChangeListener[] getPropertyChangeListeners(String arg0) {
		return propertyChangeSupport.getPropertyChangeListeners(arg0);
	}

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#hasListeners(java.lang.String)
	 */
	public boolean hasListeners(String arg0) {
		return propertyChangeSupport.hasListeners(arg0);
	}

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#removePropertyChangeListener(java.beans.PropertyChangeListener)
	 */
	public void removePropertyChangeListener(PropertyChangeListener arg0) {
		propertyChangeSupport.removePropertyChangeListener(arg0);
	}

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#removePropertyChangeListener(java.lang.String, java.beans.PropertyChangeListener)
	 */
	public void removePropertyChangeListener(String arg0,
			PropertyChangeListener arg1) {
		propertyChangeSupport.removePropertyChangeListener(arg0, arg1);
	}

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#getPageSetModel()
	 */
	public PageSetModel getPageSetModel() {
		return pageSetModel;
	}

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#setPageSetModel(jp.ticketstar.ticketing.printing.PageSetModel)
	 */
	public void setPageSetModel(PageSetModel pageSetModel) {
		final PageSetModel prevValue = this.pageSetModel;
		this.pageSetModel = pageSetModel;
		propertyChangeSupport.firePropertyChange("pageSetModel", prevValue, pageSetModel);
	}

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#getPrintService()
	 */
	public PrintService getPrintService() {
		return printService;
	}

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#setPrintService(javax.print.PrintService)
	 */
	public void setPrintService(PrintService printService) {
		final PrintService prevValue = this.printService;
		this.printService = printService;
		propertyChangeSupport.firePropertyChange("printService", prevValue, printService);
	}
	
	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#getPrintServices()
	 */
	public GenericComboBoxModel<PrintService> getPrintServices() {
		return printServices;
	}
	
	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#getPageFormat()
	 */
	public OurPageFormat getPageFormat() {
		return pageFormat;
	}

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#setPageFormat(jp.ticketstar.ticketing.printing.OurPageFormat)
	 */
	public void setPageFormat(OurPageFormat pageFormat) {
		final OurPageFormat prevValue = this.pageFormat;
		this.pageFormat = pageFormat;
		propertyChangeSupport.firePropertyChange("pageFormat", prevValue, pageFormat);
	}

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#getPageFormats()
	 */
	public GenericComboBoxModel<OurPageFormat> getPageFormats() {
		return pageFormats;
	}

	public TicketFormat getTicketFormat() {
		return ticketFormat;
	}

	public void setTicketFormat(TicketFormat ticketFormat) {
		final TicketFormat prevValue = this.ticketFormat;
		this.ticketFormat = ticketFormat;
		propertyChangeSupport.firePropertyChange("ticketFormat", prevValue, ticketFormat);
	}

	public GenericComboBoxModel<TicketFormat> getTicketFormats() {
		return ticketFormats;
	}
}