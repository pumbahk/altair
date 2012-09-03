package jp.ticketstar.ticketing.printing;

import java.io.IOException;
import java.net.URL;
import java.net.URLConnection;

public interface URLConnectionFactory {
	public URLConnection newURLConnection(URL url) throws IOException;
}
