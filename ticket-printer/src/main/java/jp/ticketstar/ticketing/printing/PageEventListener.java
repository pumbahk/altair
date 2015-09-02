package jp.ticketstar.ticketing.printing;

import java.util.EventListener;

public interface PageEventListener extends EventListener {
    public void pageAdded(PageEvent a);
    public void pageRemoved(PageEvent a);
    public void pagePrinted(PageEvent a);
}
