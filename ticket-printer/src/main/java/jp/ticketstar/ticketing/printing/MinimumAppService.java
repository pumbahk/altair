package jp.ticketstar.ticketing.printing;

import java.beans.PropertyChangeListener;
import java.util.List;

import javax.print.PrintService;

public interface MinimumAppService {
	public void printAll();

	public List<OurPageFormat> getPageFormats();
	
	public void setPageFormat(OurPageFormat pageFormat);

	public OurPageFormat getPageFormat();

	public void addListenerForPageFormat(PropertyChangeListener listener);
	
	public List<PrintService> getPrintServices();

	public void setPrintService(PrintService printService);

	public PrintService getPrintService();

	public void addListenerForPrintService(PropertyChangeListener listener);

	public List<Page> getPages();

	public void addListenerForPages(PropertyChangeListener listener);
}