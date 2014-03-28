package jp.ticketstar.ticketing.svgrpc;

import java.net.URL;
import java.io.IOException;
import java.io.ByteArrayInputStream;
import javax.servlet.ServletException;
import javax.servlet.http.Part;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.ServletConfig;
import javax.servlet.annotation.WebServlet;
import javax.servlet.annotation.MultipartConfig;
import javax.servlet.ServletContext;
import javax.portlet.ResourceRequest;
import java.io.StringReader;
import java.io.InputStreamReader;
import java.io.InputStream;

class StringHelper{
    public static String convertInputStreamToString(InputStream in) throws IOException {
        InputStreamReader reader = new InputStreamReader(in);
        StringBuilder builder = new StringBuilder();
        char[] buf = new char[4096];
        int numRead;
        while (0 <= (numRead = reader.read(buf))) {
            builder.append(buf, 0, numRead);
        }
        return builder.toString();
    }
}


@WebServlet(urlPatterns={"/raw"})
@MultipartConfig(fileSizeThreshold=5000000,maxFileSize=10000000,location="/tmp")
public class SVGRenderingRawImageServlet
    extends HttpServlet {

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws IOException, java.net.MalformedURLException, javax.servlet.ServletException{
        Part part = req.getPart("svgfile");
        String svg = StringHelper.convertInputStreamToString(part.getInputStream());

        PNGRasterizer rasterizer = new PNGRasterizer(); //setting DPI?
        rasterizer.rasterize(new StringReader(svg), resp.getOutputStream());
        resp.setContentType("image/png");
        // resp.setContentLength(res.getOutputStream().length));
    }
    public void init(ServletConfig config) throws ServletException{
        super.init(config);

        ServletContext sc = getServletContext();
    }
}
