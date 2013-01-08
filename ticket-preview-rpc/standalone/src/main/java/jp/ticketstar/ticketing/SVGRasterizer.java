package jp.ticketstar.ticketing.svgrpc;


import java.io.InputStream;
import java.io.OutputStream;

public interface SVGRasterizer{
    void rasterize(InputStream in, OutputStream out) throws AppException;
}