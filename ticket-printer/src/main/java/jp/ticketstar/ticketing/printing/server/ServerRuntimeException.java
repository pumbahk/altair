package jp.ticketstar.ticketing.printing.server;

public class ServerRuntimeException extends RuntimeException {
    private static final long serialVersionUID = 1L;

    public ServerRuntimeException() {
    }

    public ServerRuntimeException(String arg0) {
        super(arg0);
    }

    public ServerRuntimeException(Throwable arg0) {
        super(arg0);
    }

    public ServerRuntimeException(String arg0, Throwable arg1) {
        super(arg0, arg1);
    }
}
