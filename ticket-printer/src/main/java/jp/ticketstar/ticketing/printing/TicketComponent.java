package jp.ticketstar.ticketing.printing;

import jp.ticketstar.ticketing.printing.svg.JGVTComponent;

public class TicketComponent extends JGVTComponent {
	private static final long serialVersionUID = -384697470807179696L;

	public TicketComponent() {
		super();
	}

	public TicketComponent(boolean eventsEnabled, boolean selectableText) {
		super(eventsEnabled, selectableText);
	}
}
