package jp.ticketstar.ticketing.printing;

import java.util.ArrayList;
import java.util.Collection;
import java.util.Iterator;
import java.util.List;
import java.util.ListIterator;

import javax.swing.AbstractListModel;

public class Tickets extends AbstractListModel implements List<Ticket> {
	private static final long serialVersionUID = 1L;
	List<Ticket> tickets = new ArrayList<Ticket>();
	
	public Object getElementAt(int i) {
		return get(i);
	}

	public int getSize() {
		return size();
	}
	
	public void add(int arg0, Ticket arg1) {
		tickets.add(arg0, arg1);
		fireIntervalAdded(this, arg0, arg0);
	}

	public boolean add(Ticket arg0) {
		tickets.add(arg0);
		fireIntervalAdded(this, tickets.size() - 1, tickets.size() - 1);
		return true;
	}

	public boolean addAll(Collection<? extends Ticket> arg0) {
		int start = tickets.size();
		tickets.addAll(arg0);
		fireIntervalAdded(this, start, tickets.size() - 1);
		return true;
	}

	public boolean addAll(int arg0, Collection<? extends Ticket> arg1) {
		int len = arg1.size();
		tickets.addAll(arg0, arg1);
		fireIntervalAdded(this, arg0, arg0 + len - 1);
		return true;
	}

	public void clear() {
		int prevSize = size();
		tickets.clear();
		fireIntervalRemoved(this, 0, prevSize - 1);
	}

	public boolean contains(Object arg0) {
		return tickets.contains(arg0);
	}

	public boolean containsAll(Collection<?> arg0) {
		return tickets.containsAll(arg0);
	}

	public Ticket get(int arg0) {
		return tickets.get(arg0);
	}

	public int hashCode() {
		return tickets.hashCode();
	}

	public int indexOf(Object arg0) {
		return tickets.indexOf(arg0);
	}

	public boolean isEmpty() {
		return tickets.isEmpty();
	}

	public Iterator<Ticket> iterator() {
		return tickets.iterator();
	}

	public int lastIndexOf(Object arg0) {
		return tickets.lastIndexOf(arg0);
	}

	public ListIterator<Ticket> listIterator() {
		return tickets.listIterator();
	}

	public ListIterator<Ticket> listIterator(int arg0) {
		return tickets.listIterator(arg0);
	}

	public Ticket remove(int arg0) {
		return tickets.remove(arg0);
	}

	public boolean remove(Object arg0) {
		final int i = tickets.indexOf(arg0);
		if (i < 0)
			return false;
		tickets.remove(i);
		fireIntervalRemoved(this, i, i);
		return true;
	}

	public boolean removeAll(Collection<?> arg0) {
		boolean retval = false;
		for (Object item: arg0)
			retval = retval || remove(item);
		return retval;
	}

	public boolean retainAll(Collection<?> arg0) {
		return tickets.retainAll(arg0);
	}

	public Ticket set(int arg0, Ticket arg1) {
		final Ticket prevValue = tickets.set(arg0, arg1);
		if (prevValue == null || !prevValue.equals(arg1))
			fireContentsChanged(this, arg0, arg0);
		return prevValue;
	}

	public int size() {
		return tickets.size();
	}

	public List<Ticket> subList(int arg0, int arg1) {
		return tickets.subList(arg0, arg1);
	}

	public Object[] toArray() {
		return tickets.toArray();
	}

	public <T> T[] toArray(T[] arg0) {
		return tickets.toArray(arg0);
	}
}