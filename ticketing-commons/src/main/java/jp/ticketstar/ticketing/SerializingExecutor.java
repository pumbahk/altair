package jp.ticketstar.ticketing;

import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executor;
import java.util.concurrent.FutureTask;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.ThreadFactory;
import java.util.concurrent.TimeUnit;
import java.util.logging.Logger;

public class SerializingExecutor implements Executor {
	private final LinkedBlockingQueue<Runnable> queue;
	private static final Logger logger = Logger.getLogger(SerializingExecutor.class.getName());
	private volatile Thread worker;

	public SerializingExecutor(final ThreadFactory threadFactory) {
		this.queue = new LinkedBlockingQueue<Runnable>();
		this.worker = threadFactory.newThread(new Runnable() {
			public void run() {
				while (worker != null) {
					try {
						final Runnable task = queue.poll(1, TimeUnit.SECONDS);
						if (task != null) {
							try {
								task.run();
							} catch (Exception e) {
								// there's nothing more we can do...
								logger.severe(LoggingUtils.formatException(e));
							}
						}
					} catch (InterruptedException e) {
						// may be thrown when poll() is interrupted.
						break;
					}
				}
				worker = null;
			}
		});
	}

	public void start() {
		if (this.worker == null)
			throw new IllegalStateException("Executor was terminated");
		if (this.worker.isAlive())
			throw new IllegalStateException("Worker has already been started");
		this.worker.start();
	}

	public void terminate() {
		this.worker = null;
	}
	
	@Override
	public void execute(Runnable task) {
		try {
			queue.put(task);
		} catch (InterruptedException e) {
			throw new IllegalStateException(e);
		}
	}

	public <V> V executeSynchronously(Callable<V> callable) throws Exception {
		final FutureTask<V> task = new FutureTask<V>(callable);
		execute(task);
		try {
			return task.get();
		} catch (ExecutionException e) {
			if (e.getCause() instanceof Error)
				throw (Error)e.getCause();
			throw (Exception)e.getCause();
		} catch (InterruptedException e) {
			throw new IllegalStateException(e);
		}
	}

	public void executeSynchronously(final Runnable runnable) throws Exception {
		final Exception[] exceptionOccurred = new Exception[] { null };
		final Runnable wrapper = new Runnable() {
			public void run() {
				try {
					runnable.run();
				} catch (Exception e) {
					exceptionOccurred[0] = e;
				}
				synchronized (this) {
					notifyAll();
				}
			}
		};
		try {
			execute(wrapper);
			synchronized (wrapper) {
				wrapper.wait();
			}
			if (exceptionOccurred[0] != null)
				throw exceptionOccurred[0];
		} catch (InterruptedException e) {
			throw new IllegalStateException(e);
		}
	}
}
