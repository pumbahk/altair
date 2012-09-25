package jp.ticketstar.ticketing.printing;

import java.beans.PropertyChangeListener;
import java.util.List;

public interface StandardAppService extends MinimumAppService {
	public List<TicketFormat> getTicketFormats();

	public TicketFormat getTicketFormat();
	
	public void setTicketFormat(TicketFormat ticketFormat);

	public void filterByOrderId(Integer orderId);
	
	public void addListenerForTicketFormat(PropertyChangeListener listener);
}
