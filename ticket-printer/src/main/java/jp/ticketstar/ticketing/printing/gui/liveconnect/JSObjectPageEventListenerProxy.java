package jp.ticketstar.ticketing.printing.gui.liveconnect;

import java.util.Collection;

import netscape.javascript.JSObject;
import jp.ticketstar.ticketing.printing.Page;
import jp.ticketstar.ticketing.printing.PageEvent;
import jp.ticketstar.ticketing.printing.PageEventListener;

public class JSObjectPageEventListenerProxy implements PageEventListener {
    private JSObject jsobj;

    // LiveConnect は返却するオブジェクトの同一性のために、Java => JS proxy を生成時に
    // HashMap に突っ込むため、リークしてしまうから自前でも Proxy をつくる必要がある
    public static class PageProxy {
        private String name;
        private String[] queueIds;

        public String getName() {
            return name;
        }

        public String[] getQueueIds() {
            return queueIds;
        }

        private PageProxy(Page page) {
            Collection<String> _queueIds = page.getQueueIds();
            final String[] queueIds = new String[_queueIds.size()];
            _queueIds.toArray(queueIds);
            this.name = page.getName();
            this.queueIds = queueIds;
        }
    }
    
    public static class PageEventProxy {
        final PageProxy pageProxy;

        public PageProxy getPage() {
            return pageProxy;
        }
        
        private PageEventProxy(PageEvent pageEvent) {
            this.pageProxy = new PageProxy(pageEvent.getPage());
        }
    }
    
    @Override
    public void pageAdded(PageEvent evt) {
        jsobj.call("pageAdded", new Object[] { new PageEventProxy(evt) });
    }

    @Override
    public void pageRemoved(PageEvent evt) {
        jsobj.call("pageRemoved", new Object[] { new PageEventProxy(evt) });
    }

    @Override
    public void pagePrinted(PageEvent evt) {
        jsobj.call("pagePrinted", new Object[] { new PageEventProxy(evt) });
    }

    public JSObjectPageEventListenerProxy(JSObject jsobj) {
        this.jsobj = jsobj;
    }
}