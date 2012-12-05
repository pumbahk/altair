package jp.ticketstar.ticketing.svgrpc;
import java.net.URL;

public interface SVGRenderingService {
    String renderSVG(String svg, String fetchString) throws AppException;
    String renderSVG(String svg, String fetchString, String fileType) throws AppException;
    int inc(int x);
}