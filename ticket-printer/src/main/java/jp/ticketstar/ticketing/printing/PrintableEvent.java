package jp.ticketstar.ticketing.printing;

import java.awt.print.PrinterJob;
import java.awt.print.Printable;
import java.util.EventObject;

public class PrintableEvent extends EventObject {
	private static final long serialVersionUID = 1L;
	
	private PrinterJob job;
	private int pageIndex;

	public PrintableEvent(Printable printable, PrinterJob job, int pageIndex) {
		super(printable);
		this.job = job;
		this.pageIndex = pageIndex;
	}

	public PrinterJob getPrintJob() {
		return job;
	}

	public int getPageIndex() {
		return pageIndex;
	}
}
