package jp.ticketstar.ticketing.svgrpc;

import org.apache.batik.transcoder.image.PNGTranscoder;
import org.apache.batik.transcoder.TranscoderInput;
import org.apache.batik.transcoder.TranscoderOutput;
import java.io.InputStream;
import java.io.OutputStream;
public class PNGRasterizer implements SVGRasterizer{
    public void rasterize(InputStream in, OutputStream out){
        PNGTranscoder t = new PNGTranscoder();
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
