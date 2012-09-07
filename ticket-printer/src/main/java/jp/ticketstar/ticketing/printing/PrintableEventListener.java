package jp.ticketstar.ticketing.printing;

import java.util.EventListener;

public interface PrintableEventListener extends EventListener {
	void pagePrinted(PrintableEvent evt);
}
