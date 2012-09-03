package jp.ticketstar.ticketing.printing;

import java.io.IOException;
import java.io.OutputStream;

public interface RequestBodySender {
	String getRequestMethod();
	
	void send(OutputStream stream) throws IOException;
}
