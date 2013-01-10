package jp.ticketstar.ticketing.svgrpc;

import java.net.URL;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.InputStream;
import java.io.ByteArrayInputStream;
import javax.servlet.ServletException;
import javax.servlet.http.Part;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.ServletConfig;
import javax.servlet.annotation.WebServlet;
import javax.servlet.annotation.MultipartConfig;
import javax.portlet.ResourceRequest;

import com.googlecode.jsonrpc4j.JsonRpcHttpClient;

import javax.servlet.ServletContext;

class Helper{
    public static String convertInputStreamToString(InputStream in) throws IOException {
        InputStreamReader reader = new InputStreamReader(in);
        StringBuilder builder = new StringBuilder();
        char[] buf = new char[1024];
        int numRead;
        while (0 <= (numRead = reader.read(buf))) {
            builder.append(buf, 0, numRead);
        }
        return builder.toString();
    }
}

@WebServlet(urlPatterns={"/"})
@MultipartConfig(fileSizeThreshold=5000000,maxFileSize=10000000,location="/tmp")
public class SVGPreviewServlet 
    extends HttpServlet {
    private JsonRpcHttpClient rpcClient;

    @Override
        protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws IOException, java.net.MalformedURLException, javax.servlet.ServletException{
        Part part = req.getPart("svgfile");
        String svg = Helper.convertInputStreamToString(part.getInputStream());
        try{
            svg = rpcClient.invoke("normalized_xml", new Object[] {svg}, String.class);
        } catch(Throwable e){
            throw new ServletException(e);
        }
        
        PNGRasterizer rasterizer = new PNGRasterizer();
        InputStream in = new ByteArrayInputStream(svg.getBytes());
        rasterizer.rasterize(in, resp.getOutputStream());
        resp.setContentType("image/png");
        // resp.setContentLength(res.getOutputStream().length));
    }

    public void init(ServletConfig config) throws ServletException{
        super.init(config);

        ServletContext sc = getServletContext();
        try{
            this.rpcClient = new JsonRpcHttpClient(new URL("http://localhost:4445"));
        } catch (java.net.MalformedURLException e){
            throw new ServletException(e);
        }
    }
}