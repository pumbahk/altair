package jp.ticketstar.ticketing.printing;

import java.util.Iterator;
import java.util.NoSuchElementException;

import jp.ticketstar.ticketing.svg.SVGOMPageElement;
import jp.ticketstar.ticketing.svg.SVGOMPageSetElement;

import org.apache.batik.dom.AbstractElement;

public class PageElementIterator implements Iterator<SVGOMPageElement> {
    AbstractElement current;
    
    public PageElementIterator(SVGOMPageSetElement pageSet) {
        this.current = (AbstractElement) pageSet.getFirstElementChild();
        advance();
    }

    public boolean hasNext() {
        return current != null;
    }

    void advance() {
        while (current != null && !(current instanceof SVGOMPageElement))
            current = (AbstractElement)current.getNextElementSibling();
    }

    public SVGOMPageElement next() {
        if (current == null)
            throw new NoSuchElementException();
        final SVGOMPageElement retval = (SVGOMPageElement)current;
        current = (AbstractElement)current.getNextElementSibling();
        advance();
        return retval;
    }

    public void remove() {
        throw new UnsupportedOperationException();
    }
}