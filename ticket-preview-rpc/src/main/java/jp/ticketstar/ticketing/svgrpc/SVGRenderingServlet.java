package jp.ticketstar.ticketing.svgrpc;

import java.io.IOException;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.ServletConfig;
import javax.servlet.annotation.WebServlet;
import javax.portlet.ResourceRequest;

import com.googlecode.jsonrpc4j.JsonRpcServer;

import javax.servlet.ServletContext;

@WebServlet(urlPatterns={"/"})
public class SVGRenderingServlet 
    extends HttpServlet {
    private SVGRenderingService service;
    private JsonRpcServer jsonRpcServer;

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws IOException{
        jsonRpcServer.handle(req, resp);
    }

    public void init(ServletConfig config) throws ServletException{
        super.init(config);

        ServletContext sc = getServletContext();

        this.service = new SVGRenderingServiceImpl();
        this.jsonRpcServer = new JsonRpcServer(this.service, SVGRenderingService.class);
    }
}
