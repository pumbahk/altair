package jp.ticketstar.ticketing.svgrpc;

import org.apache.batik.transcoder.image.ImageTranscoder;
import org.apache.batik.transcoder.image.PNGTranscoder;
import org.apache.batik.transcoder.TranscoderInput;
import org.apache.batik.transcoder.TranscoderOutput;
import java.io.InputStream;
import java.io.OutputStream;

import jp.ticketstar.ticketing.svg.ExtendedSVG12BridgeContext;
import org.apache.batik.bridge.BridgeContext;

class ExtendedPNGTranscoder extends PNGTranscoder {
    @Override
    protected BridgeContext createBridgeContext(String svgVersion){
        if ("1.2".equals(svgVersion)){
            return new ExtendedSVG12BridgeContext(this.userAgent);
        } else {
            return new BridgeContext(this.userAgent);
        }
    }
}

public class PNGRasterizer implements SVGRasterizer{
    protected static double DOT_PER_INCH = 90.0;
    protected static double MM_PER_INCH = 25.4;
    protected static float MM_PER_PIXEL = (float)((1/DOT_PER_INCH) * MM_PER_INCH);

    public void rasterize(InputStream in, OutputStream out){
        PNGTranscoder t = new ExtendedPNGTranscoder();
        t.addTranscodingHint(ImageTranscoder.KEY_PIXEL_UNIT_TO_MILLIMETER , MM_PER_PIXEL);
        try {
            TranscoderInput input = new TranscoderInput(in);
            TranscoderOutput output = new TranscoderOutput(out);
            // Save the image.
            t.transcode(input, output);
        } catch (org.apache.batik.transcoder.TranscoderException e){
            throw new AppException(e);
        }
        finally {
            try{
                out.flush();
                out.close();
            } catch (java.io.IOException e){
                throw new AppException(e);
            }
        }        
    }
}
