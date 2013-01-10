package jp.ticketstar.ticketing.svgrpc;

public class AppException extends RuntimeException {
	private static final long serialVersionUID = 2L;

	public AppException(Throwable e) {
		super(e);
	}

	public AppException(String string) {
		super(string);
	}
}
