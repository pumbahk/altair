package jp.ticketstar.ticketing.printing.gui;

import java.util.ArrayList;
import java.util.List;
import java.util.Queue;
import java.util.concurrent.Callable;

public class QueueBundler<T> implements Callable<List<T>> {
    protected Queue<T> queue;
    protected int maxItems;

    public List<T> call() {
        List<T> retval;
        synchronized (queue) {
            retval = new ArrayList<T>(maxItems);
            for (int i = maxItems; --i >= 0;) {
                final T entry = queue.poll();
                if (entry == null)
                    break;
                retval.add(entry);
            }
        }
        return retval;
    }

    public QueueBundler(Queue<T> queue, int maxItems) {
        this.queue = queue;
        this.maxItems = maxItems;
    }
}
