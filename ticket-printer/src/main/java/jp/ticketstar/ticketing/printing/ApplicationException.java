package jp.ticketstar.ticketing.printing;

public class ApplicationException extends RuntimeException {
	private static final long serialVersionUID = 1L;

	public ApplicationException(Throwable e) {
		super(e);
	}

	public ApplicationException(String string) {
		super(string);
	}
}
