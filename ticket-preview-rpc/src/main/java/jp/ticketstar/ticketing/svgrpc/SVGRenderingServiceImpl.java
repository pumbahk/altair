package jp.ticketstar.ticketing.svgrpc;

import java.io.StringReader;
import java.io.ByteArrayOutputStream;
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

    public String renderSVG(String svg, String fileType) throws AppException{
        return this.renderSVG(svg); // not implemented yet;
    }
    public String renderSVG(String svg) throws AppException{
        SVGRasterizer rasterizer = Helper.selectRasterizer();
        ByteArrayOutputStream out = new ByteArrayOutputStream(); 
        rasterizer.rasterize(new StringReader(svg), out);
        return Base64.encodeBase64String(out.toByteArray());
    }
}
