package jp.ticketstar.ticketing.printing;

import java.awt.print.PrinterJob;
import java.beans.PropertyChangeListener;
import java.beans.PropertyChangeSupport;

import javax.print.PrintService;
import javax.swing.event.SwingPropertyChangeSupport;

public class AppWindowModel {
	PropertyChangeSupport propertyChangeSupport = new SwingPropertyChangeSupport(this, true);
	TicketSetModel ticketSetModel = null;
	PrintService printService = null;
	GenericComboBoxModel<PrintService> printServices;
	OurPageFormat pageFormat = null;
	GenericComboBoxModel<OurPageFormat> pageFormats;
	
	public AppWindowModel() {
		reload();
	}

	public void reload() {
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
			propertyChangeSupport.firePropertyChange("printService", prevPrintService, printService);
		}
		{
	        final GenericComboBoxModel<OurPageFormat> prevPageFormats = this.pageFormats;
			final GenericComboBoxModel<OurPageFormat> pageFormats = new GenericComboBoxModel<OurPageFormat>();
			pageFormats.add(PageFormatRegistry.buildPageFormatForRT());
			this.pageFormats = pageFormats;
			propertyChangeSupport.firePropertyChange("pageFormats", prevPageFormats, pageFormats);
		}
		{
			final OurPageFormat prevPageFormat = this.pageFormat;
			this.pageFormat = this.pageFormats.size() > 0 ? this.pageFormats.get(0): null;
			propertyChangeSupport.firePropertyChange("pageFormat", prevPageFormat, pageFormat);
		}
	}
	
	public void refresh() {
		propertyChangeSupport.firePropertyChange("ticketSetModel", null, ticketSetModel);
		propertyChangeSupport.firePropertyChange("printServices", null, printServices);
		propertyChangeSupport.firePropertyChange("printService", null, printService);
		propertyChangeSupport.firePropertyChange("pageFormats", null, pageFormats);
		propertyChangeSupport.firePropertyChange("pageFormat", null, pageFormat);
	}

	public void addPropertyChangeListener(PropertyChangeListener arg0) {
		propertyChangeSupport.addPropertyChangeListener(arg0);
	}

	public void addPropertyChangeListener(String arg0,
			PropertyChangeListener arg1) {
		propertyChangeSupport.addPropertyChangeListener(arg0, arg1);
	}

	public PropertyChangeListener[] getPropertyChangeListeners() {
		return propertyChangeSupport.getPropertyChangeListeners();
	}

	public PropertyChangeListener[] getPropertyChangeListeners(String arg0) {
		return propertyChangeSupport.getPropertyChangeListeners(arg0);
	}

	public boolean hasListeners(String arg0) {
		return propertyChangeSupport.hasListeners(arg0);
	}

	public void removePropertyChangeListener(PropertyChangeListener arg0) {
		propertyChangeSupport.removePropertyChangeListener(arg0);
	}

	public void removePropertyChangeListener(String arg0,
			PropertyChangeListener arg1) {
		propertyChangeSupport.removePropertyChangeListener(arg0, arg1);
	}

	public TicketSetModel getTicketSetModel() {
		return ticketSetModel;
	}

	public void setTicketSetModel(TicketSetModel ticketSetModel) {
		final TicketSetModel prevValue = this.ticketSetModel;
		this.ticketSetModel = ticketSetModel;
		propertyChangeSupport.firePropertyChange("ticketSetModel", prevValue, ticketSetModel);
	}

	public PrintService getPrintService() {
		return printService;
	}

	public void setPrintService(PrintService printService) {
		final PrintService prevValue = this.printService;
		this.printService = printService;
		propertyChangeSupport.firePropertyChange("printService", prevValue, printService);
	}
	
	public GenericComboBoxModel<PrintService> getPrintServices() {
		return printServices;
	}
	
	public OurPageFormat getPageFormat() {
		return pageFormat;
	}

	public void setPageFormat(OurPageFormat pageFormat) {
		final OurPageFormat prevValue = this.pageFormat;
		this.pageFormat = pageFormat;
		propertyChangeSupport.firePropertyChange("pageFormat", prevValue, pageFormat);
	}

	public GenericComboBoxModel<OurPageFormat> getPageFormats() {
		return pageFormats;
	}
}