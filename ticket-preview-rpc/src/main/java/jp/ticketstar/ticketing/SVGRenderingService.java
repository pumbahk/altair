package jp.ticketstar.ticketing.svgrpc;
import java.net.URL;

public interface SVGRenderingService {
    String renderSVG(String svg) throws AppException;
    String renderSVG(String svg, String fileType) throws AppException;
    int inc(int x);
}