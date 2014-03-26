package jp.ticketstar.ticketing;

import java.util.concurrent.CancellationException;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.concurrent.atomic.AtomicInteger;

public class DeferredValue<T> implements Future<T> {
	private volatile AtomicInteger status = new AtomicInteger(0);
	private volatile T result;

	@Override
	public boolean cancel(boolean mayInterruptIfRunning) {
		// TODO Auto-generated method stub
		return false;
	}

	@Override
	public T get() throws InterruptedException {
		int _status;
		_status = status.get();
		if (_status == 0) {
			synchronized (status) {
				status.wait();
			}
			_status = status.get();
		}
		if (_status >= 3)
			throw new CancellationException();
		return result;
	}

	@Override
	public T get(long timeout, TimeUnit unit) throws InterruptedException, TimeoutException {
		int _status;
		_status = status.get();
		if (_status == 0) {
			synchronized (status) {
				status.wait(unit.toMillis(timeout));
			}
			_status = status.get();
		}
		if (_status == 0)
			throw new TimeoutException();
		else if (_status >= 3)
			throw new CancellationException();
		return result;
	}

	@Override
	public boolean isCancelled() {
		return this.status.get() >= 3;
	}

	@Override
	public boolean isDone() {
		return this.status.get() >= 2;
	}

	public boolean set(T v) {
		if (!status.compareAndSet(0, 1)) {
			return false;
		}
		this.result = v;
		status.set(2);
		synchronized (status) {
			status.notifyAll();
		}
		return true;
	}
}
