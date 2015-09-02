package jp.ticketstar.ticketing.printing;

import java.util.EventObject;

public class PageEvent extends EventObject {
    private static final long serialVersionUID = 1L;

    final Page page;

    public Page getPage() {
        return page;
    }
    
    public PageEvent(Object source, Page page) {
        super(source);
        this.page = page;
    }
}
