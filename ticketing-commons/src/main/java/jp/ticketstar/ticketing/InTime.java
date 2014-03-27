package jp.ticketstar.ticketing;

import java.util.concurrent.Executor;

public final class InTime implements Executor {
	private static final InTime singleton = new InTime();

	@Override
	public void execute(Runnable command) {
		command.run();
	}

	public static InTime getInstance() {
		return singleton;
	}
}
