package jp.ticketstar.ticketing;

import java.util.ArrayList;
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
				try {
					while (worker != null) {
						final Runnable task = queue.poll(1, TimeUnit.SECONDS);
						if (task != null) {
							try {
								task.run();
							} catch (Exception e) {
								// there's nothing more we can do...
								logger.severe(LoggingUtils.formatException(e));
							}
						}
					}
				} catch (InterruptedException e) {
					// may be thrown when poll() is interrupted.
					logger.finer(LoggingUtils.formatException(e));
					worker = null;
				}
				synchronized (queue) {
					Thread.currentThread().notifyAll();
				}
			}
		});
		this.worker.setName("worker-" + getClass().getName());
	}

	protected void processQueue() {
		ArrayList<Runnable> tasksToBeDone = new ArrayList<Runnable>();
		queue.drainTo(tasksToBeDone);
		for (final Runnable task: tasksToBeDone) {
			try {
				task.run();
			} catch (Exception e) {
				// there's nothing more we can do...
				logger.severe(LoggingUtils.formatException(e));
			}
		}
	}
	
	public synchronized void start() {
		if (this.worker == null)
			throw new IllegalStateException("Executor was terminated");
		if (this.worker.isAlive())
			throw new IllegalStateException("Worker has already been started");
		this.worker.start();
	}

	public synchronized void terminate() {
		final Thread _worker = this.worker;
		this.worker = null;
		synchronized (_worker) {
			for (;;) {
				try {
					_worker.wait();
					break;
				} catch (InterruptedException e) {
					logger.finer(LoggingUtils.formatException(e));
					continue;
				}
			}
		}
	}
	
	@Override
	public void execute(Runnable task) {
		try {
			queue.put(task);
		} catch (InterruptedException e) {
			throw new IllegalStateException(e);
		}
	}

	protected <V> V executeSynchronously(final FutureTask<V> task) throws Exception {
		logger.entering(getClass().getName(), "executeSynchronously(FutureTask<V>)");
		execute(task);
		if (Thread.currentThread() == worker)
			processQueue();
		try {
			return task.get();
		} catch (ExecutionException e) {
			if (e.getCause() instanceof Error)
				throw (Error)e.getCause();
			throw (Exception)e.getCause();
		} catch (InterruptedException e) {
			throw new IllegalStateException(e);
		} finally {
			logger.exiting(getClass().getName(), "executeSynchronously(FutureTask<V>)");
		}
	}
	
	public <V> V executeSynchronously(final Callable<V> callable) throws Exception {
		return executeSynchronously(new FutureTask<V>(callable));
	}

	public void executeSynchronously(final Runnable runnable) throws Exception {
		executeSynchronously(new FutureTask<Void>(runnable, null));
	}
}
