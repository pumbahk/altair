package jp.ticketstar.ticketing.printing;

import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.geom.AffineTransform;
import java.awt.print.PrinterJob;
import java.awt.print.PageFormat;
import java.awt.print.Printable;
import java.util.List;

import jp.ticketstar.ticketing.PrintableEventListener;
import jp.ticketstar.ticketing.PrintableEventSupport;

@SuppressWarnings("static-access")
public class TicketPrintable implements Printable {
    protected static final Class<?> peekGraphicsClass;
    protected final List<Page> pages;
    protected final AffineTransform transform;
    protected final PrintableEventSupport support;

    static {
        Class<?> _peekGraphicsClass = null;
        try {
            _peekGraphicsClass = TicketPrintable.class.forName("sun.print.PeekGraphics");
        } catch (ClassNotFoundException e) {}
        peekGraphicsClass = _peekGraphicsClass;
    }
    
    public TicketPrintable(List<Page> pages, PrinterJob job) {
        this(pages, job, new AffineTransform());
    }
    
    public TicketPrintable(List<Page> pages, PrinterJob job, AffineTransform trans) {
        this.pages = pages;
        this.transform = trans;
        support = new PrintableEventSupport(this, job);
    }
    
    public int print(Graphics _g, PageFormat format, int pageIndex) {
        if (pageIndex >= pages.size())
            return NO_SUCH_PAGE;
        Graphics2D g = (Graphics2D)_g;
        g.transform(transform);
        pages.get(pageIndex).getGraphics().paint(g);
        if (peekGraphicsClass == null || !peekGraphicsClass.isInstance(_g))
            support.firePagePrintedEvent(pageIndex);
        return PAGE_EXISTS;
    }

    public void addPrintableEventListener(PrintableEventListener lsnr) {
        support.addPrintableEventListener(lsnr);
    }

    public void removePrintableEventListener(PrintableEventListener lsnr) {
        support.removePrintableEventListener(lsnr);
    }

    public List<Page> getPages() {
        return pages;
    }

    public AffineTransform getTransform() {
        return transform;
    }
}
