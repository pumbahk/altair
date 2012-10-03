package jp.ticketstar.ticketing;

import java.awt.print.PrinterJob;
import java.awt.print.Printable;
import java.util.HashSet;
import java.util.Set;

public class PrintableEventSupport {
	Printable printable;
	PrinterJob job;
	Set<PrintableEventListener> listeners = new HashSet<PrintableEventListener>();

	public void firePagePrintedEvent(int pageIndex) {
		PrintableEvent evt = new PrintableEvent(printable, job, pageIndex);
		for (PrintableEventListener lsnr: listeners) {
			lsnr.pagePrinted(evt);
		}
	}
	
	public void addPrintableEventListener(PrintableEventListener lsnr) {
		listeners.add(lsnr);
	}

	public void removePrintableEventListener(PrintableEventListener lsnr) {
		listeners.remove(lsnr);
	}

	public PrintableEventSupport(Printable printable, PrinterJob job) {
		this.printable = printable;
		this.job = job;
	}
}
