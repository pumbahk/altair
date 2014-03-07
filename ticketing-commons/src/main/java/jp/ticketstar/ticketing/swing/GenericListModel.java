package jp.ticketstar.ticketing.swing;

import java.util.ArrayList;
import java.util.Collection;
import java.util.Iterator;
import java.util.List;
import java.util.ListIterator;
import java.util.SortedSet;
import java.util.TreeSet;

import javax.swing.AbstractListModel;
import javax.swing.event.ListDataEvent;
import javax.swing.event.ListDataListener;

public class GenericListModel<T> extends AbstractListModel implements List<T> {
	private static final long serialVersionUID = 1L;
	List<T> items = new ArrayList<T>();
	
	public Object getElementAt(int i) {
		return get(i);
	}

	public int getSize() {
		return size();
	}
	
	public void add(int arg0, T arg1) {
		items.add(arg0, arg1);
		fireIntervalAdded(this, arg0, arg0);
	}

	public boolean add(T arg0) {
		items.add(arg0);
		fireIntervalAdded(this, items.size() - 1, items.size() - 1);
		return true;
	}

	public boolean addAll(Collection<? extends T> arg0) {
		int start = items.size();
		items.addAll(arg0);
		fireIntervalAdded(this, start, items.size() - 1);
		return true;
	}

	public boolean addAll(int arg0, Collection<? extends T> arg1) {
		int len = arg1.size();
		items.addAll(arg0, arg1);
		fireIntervalAdded(this, arg0, arg0 + len - 1);
		return true;
	}

	public void clear() {
		int prevSize = size();
		fireIntervalBeingRemoved(this, 0, prevSize - 1);
		items.clear();
		fireIntervalRemoved(this, 0, prevSize - 1);
	}

	public boolean contains(Object arg0) {
		return items.contains(arg0);
	}

	public boolean containsAll(Collection<?> arg0) {
		return items.containsAll(arg0);
	}

	public T get(int arg0) {
		return items.get(arg0);
	}

	public int hashCode() {
		return items.hashCode();
	}

	public int indexOf(Object arg0) {
		return items.indexOf(arg0);
	}

	public boolean isEmpty() {
		return items.isEmpty();
	}

	public Iterator<T> iterator() {
		return items.iterator();
	}

	public int lastIndexOf(Object arg0) {
		return items.lastIndexOf(arg0);
	}

	public ListIterator<T> listIterator() {
		return items.listIterator();
	}

	public ListIterator<T> listIterator(int arg0) {
		return items.listIterator(arg0);
	}

	public T remove(int arg0) {
		return items.remove(arg0);
	}

	public boolean remove(Object arg0) {
		final int i = items.indexOf(arg0);
		if (i < 0)
			return false;
		fireIntervalBeingRemoved(this, i, i);
		items.remove(i);
		fireIntervalRemoved(this, i, i);
		return true;
	}

	public boolean removeAll(Collection<?> arg0) {
		SortedSet<Integer> itemsToRemove = new TreeSet<Integer>();
		for (Object item: arg0) {
			int i = items.indexOf(item);
			itemsToRemove.add(i);
		}
		{
			int firstIndexOfContiguousChunk = 0;
			int lastIndex = -1;
			for (int i: itemsToRemove) {
				if (lastIndex + 1 != i) {
					if (lastIndex >= 0) {
						fireIntervalBeingRemoved(this, firstIndexOfContiguousChunk, lastIndex);
					}
					firstIndexOfContiguousChunk = i;
				}
				lastIndex = i;
			}
			if (lastIndex >= 0) {
				fireIntervalBeingRemoved(this, firstIndexOfContiguousChunk, lastIndex);
			}
		}
		{
			int firstIndexOfContiguousChunk = 0;
			int lastIndex = -1;
			int offset = 0;
			for (int i: itemsToRemove) {
				if (lastIndex + 1 != i) {
					if (lastIndex >= 0) {
						for (int j = lastIndex; j >= firstIndexOfContiguousChunk; j--) {
							items.remove(j);
						}
						fireIntervalRemoved(this, firstIndexOfContiguousChunk - offset, lastIndex - offset);
						offset += lastIndex - firstIndexOfContiguousChunk + 1;
					}
					firstIndexOfContiguousChunk = i;
				}
				lastIndex = i;
			}
			if (lastIndex >= 0) {
				fireIntervalRemoved(this, firstIndexOfContiguousChunk - offset, lastIndex - offset);
			}
		}
		return!!itemsToRemove.isEmpty();
	}

	public boolean retainAll(Collection<?> arg0) {
		return items.retainAll(arg0);
	}

	public T set(int arg0, T arg1) {
		final T prevValue = items.set(arg0, arg1);
		if (prevValue == null || !prevValue.equals(arg1))
			fireContentsChanged(this, arg0, arg0);
		return prevValue;
	}

	public int size() {
		return items.size();
	}

	public List<T> subList(int arg0, int arg1) {
		return items.subList(arg0, arg1);
	}

	public Object[] toArray() {
		return items.toArray();
	}

	public <E> E[] toArray(E[] arg0) {
		return items.toArray(arg0);
	}

	protected void fireIntervalBeingRemoved(Object model, int index0, int index1) {
		final ListDataEvent evt = new ListDataEvent(model, ListDataEvent.INTERVAL_REMOVED, index0, index1);
		for (ExtendedListDataListener l: listenerList.getListeners(ExtendedListDataListener.class)) {
			l.intervalBeingRemoved(evt);
		}
	}

	@Override
	public void addListDataListener(ListDataListener listener) {
		super.addListDataListener(listener);
		if (listener instanceof ExtendedListDataListener) {
			listenerList.add(ExtendedListDataListener.class, (ExtendedListDataListener)listener);
		}
	}

	@Override
	public void removeListDataListener(ListDataListener listener) {
		super.removeListDataListener(listener);
		if (listener instanceof ExtendedListDataListener) {
			listenerList.remove(ExtendedListDataListener.class, (ExtendedListDataListener)listener);
		}
	}
}
