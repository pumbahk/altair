package jp.ticketstar.ticketing.printing;

import java.io.InputStream;
import java.io.IOException;
import java.net.URLConnection;
import java.nio.ByteBuffer;

import org.apache.commons.io.IOUtils;

public class URLFetcher {
	public static class FetchResult {
		public ByteBuffer buf;
		public String contentType;
		public String encoding;

		public FetchResult(ByteBuffer buf, String contentType, String encoding) {
			this.buf = buf;
			this.contentType = contentType;
			this.encoding = encoding;
		}
	}

	public static FetchResult fetch(final URLConnection conn, RequestBodySender sender) throws IOException {
		conn.setDoOutput(sender != null);
		conn.setDoInput(true);
		if (sender != null)
			sender.send(conn.getOutputStream());
		conn.connect();
		InputStream is = conn.getInputStream();
		return new FetchResult(
			ByteBuffer.wrap(IOUtils.toByteArray(is)),
			conn.getContentType(),
			conn.getContentEncoding());
	}
}
