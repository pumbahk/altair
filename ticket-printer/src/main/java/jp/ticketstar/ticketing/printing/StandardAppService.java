package jp.ticketstar.ticketing.printing;

import java.beans.PropertyChangeListener;
import java.util.List;

public interface StandardAppService extends MinimumAppService {
    public List<TicketFormat> getTicketFormats();

    public TicketFormat getTicketFormat();
    
    public void setTicketFormat(TicketFormat ticketFormat);

    public void filterByOrderId(String orderId);
    
    public void filterByQueueIds(List<String> queueIds);
    
    public void addListenerForTicketFormat(PropertyChangeListener listener);

    public void addPageEventListener(PageEventListener listener);
}
