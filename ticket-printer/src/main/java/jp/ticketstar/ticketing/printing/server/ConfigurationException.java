package jp.ticketstar.ticketing.printing.server;

public class ConfigurationException extends RuntimeException {
    private static final long serialVersionUID = 1L;

    public ConfigurationException() {
        super();
    }

    public ConfigurationException(String arg0, Throwable arg1) {
        super(arg0, arg1);
    }

    public ConfigurationException(String arg0) {
        super(arg0);
    }

    public ConfigurationException(Throwable arg0) {
        super(arg0);
    }
}