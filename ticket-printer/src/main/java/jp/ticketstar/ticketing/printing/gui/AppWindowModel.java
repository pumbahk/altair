package jp.ticketstar.ticketing.printing.gui;

import java.awt.print.PageFormat;
import java.awt.print.PrinterJob;
import java.beans.PropertyChangeListener;
import java.beans.PropertyChangeSupport;

import javax.print.PrintService;
import javax.swing.event.SwingPropertyChangeSupport;

import jp.ticketstar.ticketing.NESW;
import jp.ticketstar.ticketing.PrintingUtils;
import jp.ticketstar.ticketing.UnitUtils;
import jp.ticketstar.ticketing.DDimension2D;
import jp.ticketstar.ticketing.swing.GenericComboBoxModel;
import jp.ticketstar.ticketing.printing.AppModel;
import jp.ticketstar.ticketing.printing.OurPageFormat;
import jp.ticketstar.ticketing.printing.PageSetModel;

public class AppWindowModel implements AppModel {
	PropertyChangeSupport propertyChangeSupport = new SwingPropertyChangeSupport(this, true);
	PageSetModel pageSetModel = null;
	PrintService printService = null;
	GenericComboBoxModel<PrintService> printServices;
	OurPageFormat pageFormat = null;
	GenericComboBoxModel<OurPageFormat> pageFormats;
	
	public AppWindowModel() {
		initialize();
	}
	
    static OurPageFormat buildPageFormatForRT() {
        final OurPageFormat retval = new OurPageFormat();
        retval.setName("楽天チケット");
        retval.setVerticalGuides(new double[] { UnitUtils.mmToPoint(17.8), UnitUtils.mmToPoint(139) });
        retval.setPaper(PrintingUtils.buildPaper(new DDimension2D(UnitUtils.mmToPoint(65.04), UnitUtils.mmToPoint(177.96))));
        retval.setOrientation(PageFormat.LANDSCAPE);
        return retval;
    }
   
    static OurPageFormat buildPageFormatA4Portrait() {
    	final OurPageFormat retval = new OurPageFormat();
    	retval.setName("A4タテ");
    	retval.setPaper(PrintingUtils.buildPaper(
    			new DDimension2D(UnitUtils.mmToPoint(210), UnitUtils.mmToPoint(297)),
    			new NESW(UnitUtils.mmToPoint(20), UnitUtils.mmToPoint(20))));
    	retval.setOrientation(PageFormat.PORTRAIT);
    	return retval;
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
			propertyChangeSupport.firePropertyChange("printService", prevPrintService, printService);
		}
		{
	        final GenericComboBoxModel<OurPageFormat> prevPageFormats = this.pageFormats;
			final GenericComboBoxModel<OurPageFormat> pageFormats = new GenericComboBoxModel<OurPageFormat>();
			pageFormats.add(buildPageFormatForRT());
			pageFormats.add(buildPageFormatA4Portrait());
			this.pageFormats = pageFormats;
			propertyChangeSupport.firePropertyChange("pageFormats", prevPageFormats, pageFormats);
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
	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppModel#refresh()
	 */
	public void refresh() {
		propertyChangeSupport.firePropertyChange("pageSetModel", null, pageSetModel);
		propertyChangeSupport.firePropertyChange("printServices", null, printServices);
		propertyChangeSupport.firePropertyChange("printService", null, printService);
		propertyChangeSupport.firePropertyChange("pageFormats", null, pageFormats);
		propertyChangeSupport.firePropertyChange("pageFormat", null, pageFormat);
	}

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#addPropertyChangeListener(java.beans.PropertyChangeListener)
	 */
	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppModel#addPropertyChangeListener(java.beans.PropertyChangeListener)
	 */
	public void addPropertyChangeListener(PropertyChangeListener arg0) {
		propertyChangeSupport.addPropertyChangeListener(arg0);
	}

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#addPropertyChangeListener(java.lang.String, java.beans.PropertyChangeListener)
	 */
	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppModel#addPropertyChangeListener(java.lang.String, java.beans.PropertyChangeListener)
	 */
	public void addPropertyChangeListener(String arg0,
			PropertyChangeListener arg1) {
		propertyChangeSupport.addPropertyChangeListener(arg0, arg1);
	}

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#getPropertyChangeListeners()
	 */
	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppModel#getPropertyChangeListeners()
	 */
	public PropertyChangeListener[] getPropertyChangeListeners() {
		return propertyChangeSupport.getPropertyChangeListeners();
	}

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#getPropertyChangeListeners(java.lang.String)
	 */
	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppModel#getPropertyChangeListeners(java.lang.String)
	 */
	public PropertyChangeListener[] getPropertyChangeListeners(String arg0) {
		return propertyChangeSupport.getPropertyChangeListeners(arg0);
	}

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#hasListeners(java.lang.String)
	 */
	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppModel#hasListeners(java.lang.String)
	 */
	public boolean hasListeners(String arg0) {
		return propertyChangeSupport.hasListeners(arg0);
	}

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#removePropertyChangeListener(java.beans.PropertyChangeListener)
	 */
	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppModel#removePropertyChangeListener(java.beans.PropertyChangeListener)
	 */
	public void removePropertyChangeListener(PropertyChangeListener arg0) {
		propertyChangeSupport.removePropertyChangeListener(arg0);
	}

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#removePropertyChangeListener(java.lang.String, java.beans.PropertyChangeListener)
	 */
	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppModel#removePropertyChangeListener(java.lang.String, java.beans.PropertyChangeListener)
	 */
	public void removePropertyChangeListener(String arg0,
			PropertyChangeListener arg1) {
		propertyChangeSupport.removePropertyChangeListener(arg0, arg1);
	}

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#getPageSetModel()
	 */
	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppModel#getPageSetModel()
	 */
	public PageSetModel getPageSetModel() {
		return pageSetModel;
	}

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#setPageSetModel(jp.ticketstar.ticketing.printing.PageSetModel)
	 */
	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppModel#setPageSetModel(jp.ticketstar.ticketing.printing.PageSetModel)
	 */
	public void setPageSetModel(PageSetModel pageSetModel) {
		final PageSetModel prevValue = this.pageSetModel;
		this.pageSetModel = pageSetModel;
		propertyChangeSupport.firePropertyChange("pageSetModel", prevValue, pageSetModel);
	}

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#getPrintService()
	 */
	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppModel#getPrintService()
	 */
	public PrintService getPrintService() {
		return printService;
	}

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#setPrintService(javax.print.PrintService)
	 */
	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppModel#setPrintService(javax.print.PrintService)
	 */
	public void setPrintService(PrintService printService) {
		final PrintService prevValue = this.printService;
		this.printService = printService;
		propertyChangeSupport.firePropertyChange("printService", prevValue, printService);
	}
	
	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#getPrintServices()
	 */
	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppModel#getPrintServices()
	 */
	public GenericComboBoxModel<PrintService> getPrintServices() {
		return printServices;
	}
	
	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#getPageFormat()
	 */
	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppModel#getPageFormat()
	 */
	public OurPageFormat getPageFormat() {
		return pageFormat;
	}

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#setPageFormat(jp.ticketstar.ticketing.printing.OurPageFormat)
	 */
	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppModel#setPageFormat(jp.ticketstar.ticketing.printing.OurPageFormat)
	 */
	public void setPageFormat(OurPageFormat pageFormat) {
		final OurPageFormat prevValue = this.pageFormat;
		this.pageFormat = pageFormat;
		propertyChangeSupport.firePropertyChange("pageFormat", prevValue, pageFormat);
	}

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#getPageFormats()
	 */
	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppModel#getPageFormats()
	 */
	public GenericComboBoxModel<OurPageFormat> getPageFormats() {
		return pageFormats;
	}
}