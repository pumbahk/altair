package jp.ticketstar.ticketing.svgrpc;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import org.apache.commons.codec.binary.Base64;

class Helper {
    protected static SVGRasterizer selectRasterizer(String filetype){
        return new PNGRasterizer(); //todo not implemented
    }
    protected static SVGRasterizer selectRasterizer(){
        return new PNGRasterizer();
    }
}

public class SVGRenderingServiceImpl implements SVGRenderingService{
    public int inc(int x){
        return x + 1;
    }

    public String renderSVG(String svg, String fetchString, String fileType) throws AppException{
        return this.renderSVG(svg, fetchString); // not implemented yet;
    }
    public String renderSVG(String svg, String fetchString) throws AppException{
        SVGRasterizer rasterizer = Helper.selectRasterizer();
        InputStream in = new ByteArrayInputStream(svg.getBytes());
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        rasterizer.rasterize(in, out);
        return Base64.encodeBase64String(out.toByteArray());
    }
}
