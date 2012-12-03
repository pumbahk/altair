package jp.ticketstar.ticketing.svgrpc;

import javax.servlet.http.HttpServletResponse;
import java.io.FileInputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.File;
import java.io.IOException;

public class ImageWriter{
    private String filename;
    private String mimeType;

    ImageWriter(String filename, String mimeType){
        this.filename = filename;
        this.mimeType = mimeType;
    }

    private void writeData(InputStream in, OutputStream out) throws IOException{
        byte[] buf = new byte[4096];
        int count = 0;
        while ((count = in.read(buf)) >= 0) {
            out.write(buf, 0, count);
        }
        in.close();
        out.close();
    }

    public void writeResponse(HttpServletResponse resp) throws IOException{
        resp.setContentType(mimeType);
        File file = new File(filename);
        resp.setContentLength((int)file.length());
        OutputStream out = resp.getOutputStream();
        writeData(new FileInputStream(file), out);
    }
}
