package jp.ticketstar.ticketing.swing;

import javax.swing.event.ListDataEvent;
import javax.swing.event.ListDataListener;

public interface ExtendedListDataListener extends ListDataListener {
	public void intervalBeingRemoved(ListDataEvent evt);
}
