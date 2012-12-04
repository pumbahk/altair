package jp.ticketstar.ticketing.svgrpc;

import java.io.ByteArrayInputStream;
import java.io.File;
import java.io.InputStream;
import java.io.FileOutputStream;
import java.io.OutputStream;
import java.util.UUID;
import java.net.URL;

class Helper {
    protected static SVGRasterizer selectRasterizer(String filetype){
        return new PNGRasterizer(); //todo not implemented
    }
    protected static SVGRasterizer selectRasterizer(){
        return new PNGRasterizer();
    }

    protected static String createOutputName(String rootDir){ // todo: move
        String fnamePeace = UUID.randomUUID().toString();
        // String fnamePeace = "hey";
        return rootDir+"/"+fnamePeace+".png";
    }
}

public class SVGRenderingServiceImpl implements SVGRenderingService{
    private String rootDir;

    SVGRenderingServiceImpl(String rootDir){
        this.rootDir = rootDir;
    }

    public int inc(int x){
        return x + 1;
    }

    public URL renderSVG(String svg, String fetchURL, String fileType) throws AppException{
        return this.renderSVG(svg, fetchURL); // not implemented yet;
    }
    public URL renderSVG(String svg, String fetchURL) throws AppException{
        SVGRasterizer rasterizer = Helper.selectRasterizer();
        InputStream in = new ByteArrayInputStream(svg.getBytes());
        String outname = Helper.createOutputName(this.rootDir);

        try{
            OutputStream out = new FileOutputStream(outname);
            
            rasterizer.rasterize(in, out);
            return new URL(fetchURL+"?filename="+(new File(outname).getName()));
        } catch(java.net.MalformedURLException e){
            throw new AppException(e);
        } catch(java.io.FileNotFoundException e){
            throw new AppException(e);
        }
    }
}
