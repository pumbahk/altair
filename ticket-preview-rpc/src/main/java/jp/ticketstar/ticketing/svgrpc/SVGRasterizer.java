package jp.ticketstar.ticketing.svgrpc;


import java.io.Reader;
import java.io.OutputStream;

public interface SVGRasterizer{
    void rasterize(Reader in, OutputStream out) throws AppException;
}
