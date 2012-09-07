package jp.ticketstar.ticketing.printing;

import java.beans.PropertyChangeListener;

import javax.print.PrintService;


public interface AppModel {

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#reload()
	 */
	public abstract void initialize();

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#refresh()
	 */
	public abstract void refresh();

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#addPropertyChangeListener(java.beans.PropertyChangeListener)
	 */
	public abstract void addPropertyChangeListener(PropertyChangeListener arg0);

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#addPropertyChangeListener(java.lang.String, java.beans.PropertyChangeListener)
	 */
	public abstract void addPropertyChangeListener(String arg0,
			PropertyChangeListener arg1);

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#getPropertyChangeListeners()
	 */
	public abstract PropertyChangeListener[] getPropertyChangeListeners();

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#getPropertyChangeListeners(java.lang.String)
	 */
	public abstract PropertyChangeListener[] getPropertyChangeListeners(
			String arg0);

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#hasListeners(java.lang.String)
	 */
	public abstract boolean hasListeners(String arg0);

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#removePropertyChangeListener(java.beans.PropertyChangeListener)
	 */
	public abstract void removePropertyChangeListener(
			PropertyChangeListener arg0);

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#removePropertyChangeListener(java.lang.String, java.beans.PropertyChangeListener)
	 */
	public abstract void removePropertyChangeListener(String arg0,
			PropertyChangeListener arg1);

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#getTicketSetModel()
	 */
	public abstract PageSetModel getPageSetModel();

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#setTicketSetModel(jp.ticketstar.ticketing.printing.TicketSetModel)
	 */
	public abstract void setPageSetModel(PageSetModel pageSetModel);

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#getPrintService()
	 */
	public abstract PrintService getPrintService();

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#setPrintService(javax.print.PrintService)
	 */
	public abstract void setPrintService(PrintService printService);

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#getPrintServices()
	 */
	public abstract GenericComboBoxModel<PrintService> getPrintServices();

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#getPageFormat()
	 */
	public abstract OurPageFormat getPageFormat();

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#setPageFormat(jp.ticketstar.ticketing.printing.OurPageFormat)
	 */
	public abstract void setPageFormat(OurPageFormat pageFormat);

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#getPageFormats()
	 */
	public abstract GenericComboBoxModel<OurPageFormat> getPageFormats();

}