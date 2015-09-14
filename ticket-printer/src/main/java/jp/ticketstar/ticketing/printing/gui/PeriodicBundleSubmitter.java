package jp.ticketstar.ticketing.printing.gui;

import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Future;
import java.util.concurrent.FutureTask;
import java.util.concurrent.RunnableFuture;
import java.util.logging.Logger;

import jp.ticketstar.ticketing.DeferredValue;
import jp.ticketstar.ticketing.LoggingUtils;

public class PeriodicBundleSubmitter<T> {
    protected static Logger logger = Logger.getLogger(PeriodicBundleSubmitter.class.getName());

    public interface BundleHandler<T> {
        public void handle(List<T> bundle);
    }

    protected Callable<List<T>> bundler;
    protected BundleHandler<T> bundleHandler;
    protected long interval;

    private class Task implements Runnable {
        private Future<Future<?>> futureRetriever;

        public void run() {
            try {
                final Future<?> future = futureRetriever.get();
                while (!future.isDone()) {
                    final long time = System.currentTimeMillis();
                    try {
                        List<T> bundle = bundler.call();
                        if (bundle.size() > 0)
                            bundleHandler.handle(bundle);
                    } catch (Exception e) {
                        logger.warning(LoggingUtils.formatException(e));
                    }
                    final long timeToSleep = (time + interval) - System.currentTimeMillis();
                    if (timeToSleep > 0)
                        Thread.sleep(timeToSleep);
                }
            } catch (InterruptedException e) {
            } catch (ExecutionException e) {
            } finally {
            }
        }

        public Task(Future<Future<?>> futureRetriever) {
            this.futureRetriever = futureRetriever;
        }
    }
    
    public RunnableFuture<?> yield() {
        final DeferredValue<Future<?>> retriever = new DeferredValue<Future<?>>();
        final RunnableFuture<?> retval = new FutureTask<Void>(new Task(retriever), null);
        retriever.set(retval);
        return retval;
    }

    public PeriodicBundleSubmitter(Callable<List<T>> bundler, BundleHandler<T> bundleHandler, long interval) {
        this.bundler = bundler;
        this.bundleHandler = bundleHandler;
        this.interval = interval;
    }
}
