package jp.ticketstar.ticketing;

import java.util.EventListener;

public interface PrintableEventListener extends EventListener {
	void pagePrinted(PrintableEvent evt);
}
